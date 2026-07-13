-- ============================================================================
-- File:     analytics_pipeline.sql
-- Summary:  Designs and implements the Enterprise Analytics Layer.
--           Builds a dependency chain of reusable dimensional and fact views.
--           Provides clean, aggregated, and dashboard-ready reporting datasets.
-- ============================================================================

-- Create a dedicated analytics schema to isolate analytical reporting from operational tables
CREATE SCHEMA IF NOT EXISTS analytics;

-- ----------------------------------------------------------------------------
-- STAGE 1: DIMENSIONAL LAYER (Base entities for joining across domains)
-- ----------------------------------------------------------------------------

-- View 1: Calendar Dimension View
-- Extracts dates from minimum to maximum transactions to build a continuous date lookup table.
CREATE OR REPLACE VIEW analytics.calendar_dim AS
WITH date_range AS (
    SELECT MIN(OrderDate)::date AS min_date, MAX(OrderDate)::date AS max_date
    FROM sales.salesorderheader
),
generated_dates AS (
    SELECT generate_series(min_date, max_date, '1 day'::interval)::date AS date_key
    FROM date_range
)
SELECT 
    date_key,
    EXTRACT(YEAR FROM date_key)::int AS year,
    EXTRACT(QUARTER FROM date_key)::int AS quarter,
    EXTRACT(MONTH FROM date_key)::int AS month,
    TRIM(TO_CHAR(date_key, 'Month')) AS month_name,
    EXTRACT(DAY FROM date_key)::int AS day_of_month,
    TRIM(TO_CHAR(date_key, 'Day')) AS day_name,
    CASE WHEN EXTRACT(ISODOW FROM date_key) IN (6, 7) THEN TRUE ELSE FALSE END AS is_weekend
FROM generated_dates;

-- View 2: Product Dimension View
-- Consolidates products with subcategories and categories; calculates markup potential.
CREATE OR REPLACE VIEW analytics.product_dim AS
SELECT 
    p.ProductID,
    p.Name AS product_name,
    p.ProductNumber,
    p.Color,
    p.StandardCost,
    p.ListPrice,
    COALESCE(p.ListPrice - p.StandardCost, 0.0) AS potential_margin,
    CASE 
        WHEN p.StandardCost > 0 THEN ROUND(((p.ListPrice - p.StandardCost) / p.StandardCost) * 100, 2)
        ELSE 0.0
    END AS markup_percentage,
    ps.ProductSubcategoryID,
    ps.Name AS subcategory_name,
    pc.ProductCategoryID,
    pc.Name AS category_name,
    p.SellStartDate::date AS sell_start_date,
    p.SellEndDate::date AS sell_end_date,
    CASE 
        WHEN p.SellEndDate IS NULL THEN 'Active'
        ELSE 'Discontinued'
    END AS status
FROM production.product p
LEFT JOIN production.productsubcategory ps ON p.productsubcategoryid = ps.productsubcategoryid
LEFT JOIN production.productcategory pc ON ps.productcategoryid = pc.productcategoryid;

-- View 3: Customer Dimension View
-- Merges customers, individual details, and store details into a single clean lookup.
CREATE OR REPLACE VIEW analytics.customer_dim AS
SELECT 
    c.CustomerID,
    c.PersonID,
    c.StoreID,
    c.TerritoryID,
    CASE 
        WHEN c.PersonID IS NOT NULL THEN TRIM(CONCAT_WS(' ', p.FirstName, p.MiddleName, p.LastName))
        WHEN c.StoreID IS NOT NULL THEN s.Name
        ELSE 'Unknown Customer'
    END AS customer_name,
    CASE 
        WHEN c.PersonID IS NOT NULL AND c.StoreID IS NULL THEN 'Individual'
        WHEN c.StoreID IS NOT NULL AND c.PersonID IS NULL THEN 'Retail Store'
        WHEN c.StoreID IS NOT NULL AND c.PersonID IS NOT NULL THEN 'Store Contact'
        ELSE 'Other'
    END AS customer_type,
    t.Name AS territory_name,
    t.CountryRegionCode,
    t.Group AS territory_group
FROM sales.customer c
LEFT JOIN person.person p ON c.personid = p.businessentityid
LEFT JOIN sales.store s ON c.storeid = s.businessentityid
LEFT JOIN sales.salesterritory t ON c.territoryid = t.territoryid;

-- View 4: Sales Person Dimension View
-- Consolidates salespeople, employee details, and names.
CREATE OR REPLACE VIEW analytics.sales_person_dim AS
SELECT 
    sp.BusinessEntityID AS salesperson_id,
    TRIM(CONCAT_WS(' ', p.FirstName, p.MiddleName, p.LastName)) AS salesperson_name,
    e.JobTitle,
    e.Gender,
    e.HireDate::date AS hire_date,
    sp.TerritoryID,
    t.Name AS territory_name,
    sp.SalesQuota,
    sp.Bonus,
    sp.CommissionPct,
    sp.SalesYTD,
    sp.SalesLastYear
FROM sales.salesperson sp
INNER JOIN humanresources.employee e ON sp.businessentityid = e.businessentityid
INNER JOIN person.person p ON sp.businessentityid = p.businessentityid
LEFT JOIN sales.salesterritory t ON sp.territoryid = t.territoryid;


-- ----------------------------------------------------------------------------
-- STAGE 2: FACT LAYER (Granular transaction details linked to dimensions)
-- ----------------------------------------------------------------------------

-- View 5: Sales Fact View
-- Flattens sales transactions, computes sales values, discounts, and allocates tax/freight proportionally.
CREATE OR REPLACE VIEW analytics.sales_fact AS
SELECT 
    sod.SalesOrderID,
    sod.SalesOrderDetailID,
    soh.OrderDate::date AS order_date,
    soh.CustomerID,
    soh.SalesPersonID,
    soh.TerritoryID,
    sod.ProductID,
    sod.OrderQty,
    sod.UnitPrice,
    sod.UnitPriceDiscount,
    -- Line subtotal before tax and freight, after discount
    (sod.UnitPrice * (1.0 - sod.UnitPriceDiscount) * sod.OrderQty) AS line_subtotal,
    -- Cost of Goods Sold (COGS)
    (p.StandardCost * sod.OrderQty) AS line_cogs,
    -- Allocated Tax and Freight (proportional to line contribution to total subtotal)
    CASE 
        WHEN soh.SubTotal > 0 THEN 
            ROUND(((sod.UnitPrice * (1.0 - sod.UnitPriceDiscount) * sod.OrderQty) / soh.SubTotal) * soh.TaxAmt, 4)
        ELSE 0.0
    END AS allocated_tax,
    CASE 
        WHEN soh.SubTotal > 0 THEN 
            ROUND(((sod.UnitPrice * (1.0 - sod.UnitPriceDiscount) * sod.OrderQty) / soh.SubTotal) * soh.Freight, 4)
        ELSE 0.0
    END AS allocated_freight,
    -- Net actual revenue for this line
    (sod.UnitPrice * (1.0 - sod.UnitPriceDiscount) * sod.OrderQty) AS net_sales_amount,
    -- Gross profit for this line
    ((sod.UnitPrice * (1.0 - sod.UnitPriceDiscount) * sod.OrderQty) - (p.StandardCost * sod.OrderQty)) AS gross_profit
FROM sales.salesorderdetail sod
INNER JOIN sales.salesorderheader soh ON sod.salesorderid = soh.salesorderid
INNER JOIN production.product p ON sod.productid = p.productid;

-- View 6: Purchasing Fact View
-- Flattens purchase transactions, computes lead times and rejection ratios.
CREATE OR REPLACE VIEW analytics.purchasing_fact AS
SELECT 
    pod.PurchaseOrderID,
    pod.PurchaseOrderDetailID,
    poh.OrderDate::date AS order_date,
    poh.VendorID,
    v.Name AS vendor_name,
    pod.ProductID,
    pod.OrderQty,
    pod.UnitPrice,
    (pod.OrderQty * pod.UnitPrice) AS purchase_amount,
    pod.ReceivedQty,
    pod.RejectedQty,
    poh.ShipDate::date AS ship_date,
    pod.DueDate::date AS due_date,
    -- Lead time in days
    CASE 
        WHEN poh.ShipDate IS NOT NULL THEN (poh.ShipDate::date - poh.OrderDate::date)
        ELSE NULL
    END AS lead_time_days
FROM purchasing.purchaseorderdetail pod
INNER JOIN purchasing.purchaseorderheader poh ON pod.purchaseorderid = poh.purchaseorderid
INNER JOIN purchasing.vendor v ON poh.vendorid = v.businessentityid;


-- ----------------------------------------------------------------------------
-- STAGE 3: AGGREGATED ANALYTICS LAYER (Business Metrics & Segmentation)
-- ----------------------------------------------------------------------------

-- View 7: Monthly Revenue View (Sales Analytics)
-- Computes aggregated monthly sales, average order value, and Month-over-Month (MoM) growth.
CREATE OR REPLACE VIEW analytics.monthly_revenue AS
WITH monthly_sales AS (
    SELECT 
        c.year,
        c.month,
        c.month_name,
        SUM(f.net_sales_amount) AS monthly_revenue,
        COUNT(DISTINCT f.SalesOrderID) AS order_count,
        SUM(f.OrderQty) AS units_sold,
        SUM(f.gross_profit) AS monthly_gross_profit
    FROM analytics.sales_fact f
    INNER JOIN analytics.calendar_dim c ON f.order_date = c.date_key
    GROUP BY c.year, c.month, c.month_name
)
SELECT 
    year,
    month,
    month_name,
    monthly_revenue,
    order_count,
    units_sold,
    monthly_gross_profit,
    ROUND(monthly_revenue / NULLIF(order_count, 0), 2) AS average_order_value,
    -- MoM revenue change and percentage growth using LAG() window functions
    LAG(monthly_revenue) OVER (ORDER BY year, month) AS previous_month_revenue,
    COALESCE(monthly_revenue - LAG(monthly_revenue) OVER (ORDER BY year, month), 0.0) AS mom_revenue_change,
    ROUND(
        COALESCE(
            ((monthly_revenue - LAG(monthly_revenue) OVER (ORDER BY year, month)) / NULLIF(LAG(monthly_revenue) OVER (ORDER BY year, month), 0.0)) * 100, 
            0.0
        ), 
        2
    ) AS mom_revenue_growth_pct
FROM monthly_sales;

-- View 8: Customer Metrics & RFM Segmentation View (Customer Analytics)
-- Computes Customer Lifetime Value (CLV), purchase frequency, recency, and RFM-based segments.
CREATE OR REPLACE VIEW analytics.customer_clv_segments AS
WITH customer_raw_metrics AS (
    SELECT 
        CustomerID,
        SUM(net_sales_amount) AS total_spend,
        COUNT(DISTINCT SalesOrderID) AS order_count,
        SUM(OrderQty) AS total_items_purchased,
        MAX(order_date) AS last_purchase_date,
        -- Recency: Days since last purchase relative to overall database maximum date
        (SELECT MAX(order_date) FROM analytics.sales_fact) - MAX(order_date) AS recency_days
    FROM analytics.sales_fact
    GROUP BY CustomerID
),
customer_ranks AS (
    SELECT 
        m.*,
        c.customer_name,
        c.customer_type,
        c.territory_name,
        -- RFM scores from 1 to 5 (5 is best)
        NTILE(5) OVER (ORDER BY m.recency_days ASC) AS r_score,      -- Low recency is best
        NTILE(5) OVER (ORDER BY m.order_count DESC) AS f_score,     -- High frequency is best
        NTILE(5) OVER (ORDER BY m.total_spend DESC) AS m_score      -- High monetary value is best
    FROM customer_raw_metrics m
    INNER JOIN analytics.customer_dim c ON m.CustomerID = c.CustomerID
)
SELECT 
    CustomerID,
    customer_name,
    customer_type,
    territory_name,
    total_spend AS customer_lifetime_value,
    order_count AS purchase_frequency,
    total_items_purchased,
    last_purchase_date,
    recency_days,
    CASE 
        WHEN order_count > 1 THEN TRUE
        ELSE FALSE
    END AS is_repeat_customer,
    -- Segmentation logic based on combined F & M scores
    CASE 
        WHEN (f_score + m_score) >= 9 THEN 'Platinum (VIP)'
        WHEN (f_score + m_score) >= 7 THEN 'Gold (Loyal)'
        WHEN (f_score + m_score) >= 4 THEN 'Silver (Steady)'
        ELSE 'Bronze (Occasional)'
    END AS customer_segment
FROM customer_ranks;

-- View 9: Product Profitability & Rankings View (Product Analytics)
-- Analyzes sales volume, margins, standard costs, and rankings within each product category.
CREATE OR REPLACE VIEW analytics.product_profitability AS
WITH product_sales AS (
    SELECT 
        ProductID,
        SUM(OrderQty) AS total_units_sold,
        SUM(net_sales_amount) AS total_revenue,
        SUM(line_cogs) AS total_cogs,
        SUM(gross_profit) AS total_profit
    FROM analytics.sales_fact
    GROUP BY ProductID
)
SELECT 
    pd.ProductID,
    pd.product_name,
    pd.category_name,
    pd.subcategory_name,
    pd.StandardCost,
    pd.ListPrice,
    COALESCE(ps.total_units_sold, 0) AS total_units_sold,
    COALESCE(ps.total_revenue, 0.0) AS total_revenue,
    COALESCE(ps.total_cogs, 0.0) AS total_cogs,
    COALESCE(ps.total_profit, 0.0) AS total_profit,
    ROUND(
        CASE 
            WHEN COALESCE(ps.total_revenue, 0.0) > 0 THEN 
                (ps.total_profit / ps.total_revenue) * 100
            ELSE 0.0
        END, 
        2
    ) AS realized_gross_margin_pct,
    -- Rank products by profitability inside each category using DENSE_RANK()
    DENSE_RANK() OVER (
        PARTITION BY pd.category_name 
        ORDER BY COALESCE(ps.total_profit, 0.0) DESC
    ) AS profit_rank_in_category
FROM analytics.product_dim pd
LEFT JOIN product_sales ps ON pd.ProductID = ps.ProductID;

-- View 10: Territory Performance View (Territory Analytics)
-- Computes territory contribution percentages and lists territory ranking.
CREATE OR REPLACE VIEW analytics.territory_sales AS
WITH territory_monthly AS (
    SELECT 
        c.year,
        c.month,
        cd.territory_group,
        cd.CountryRegionCode,
        cd.territory_name,
        SUM(sf.net_sales_amount) AS revenue,
        COUNT(DISTINCT sf.SalesOrderID) AS order_count
    FROM analytics.sales_fact sf
    INNER JOIN analytics.customer_dim cd ON sf.CustomerID = cd.CustomerID
    INNER JOIN analytics.calendar_dim c ON sf.order_date = c.date_key
    GROUP BY c.year, c.month, cd.territory_group, cd.CountryRegionCode, cd.territory_name
),
territory_totals AS (
    SELECT 
        territory_name,
        territory_group,
        CountryRegionCode,
        SUM(revenue) AS total_revenue,
        SUM(order_count) AS total_orders,
        DENSE_RANK() OVER (ORDER BY SUM(revenue) DESC) AS revenue_rank
    FROM territory_monthly
    GROUP BY territory_name, territory_group, CountryRegionCode
)
SELECT 
    t.territory_name,
    t.territory_group,
    t.CountryRegionCode,
    t.total_revenue,
    t.total_orders,
    t.revenue_rank,
    ROUND(t.total_revenue / NULLIF(SUM(t.total_revenue) OVER (), 0) * 100, 2) AS revenue_contribution_pct
FROM territory_totals t;

-- View 11: Salesperson Rankings & Quota Attainment View (Employee Analytics)
-- Tracks sales representative achievements, ranks them, and calculates commissions.
CREATE OR REPLACE VIEW analytics.salesperson_performance AS
WITH person_sales AS (
    SELECT 
        SalesPersonID,
        SUM(net_sales_amount) AS total_sales,
        COUNT(DISTINCT SalesOrderID) AS total_orders,
        SUM(gross_profit) AS total_profit
    FROM analytics.sales_fact
    WHERE SalesPersonID IS NOT NULL
    GROUP BY SalesPersonID
)
SELECT 
    spd.salesperson_id,
    spd.salesperson_name,
    spd.JobTitle,
    spd.territory_name,
    spd.SalesQuota,
    COALESCE(ps.total_sales, 0.0) AS actual_sales_ytd,
    COALESCE(ps.total_orders, 0) AS total_orders,
    COALESCE(ps.total_profit, 0.0) AS total_profit,
    ROUND(
        CASE 
            WHEN spd.SalesQuota > 0 THEN 
                (COALESCE(ps.total_sales, 0.0) / spd.SalesQuota) * 100
            ELSE NULL
        END, 
        2
    ) AS quota_attainment_pct,
    ROUND(COALESCE(ps.total_sales, 0.0) * spd.CommissionPct, 2) AS commission_earned,
    DENSE_RANK() OVER (ORDER BY COALESCE(ps.total_sales, 0.0) DESC) AS sales_rank
FROM analytics.sales_person_dim spd
LEFT JOIN person_sales ps ON spd.salesperson_id = ps.SalesPersonID;

-- View 12: Inventory Health View (Inventory Analytics)
-- Assesses current warehouse quantities against safety limits and flags out-of-stock or overstocked lines.
CREATE OR REPLACE VIEW analytics.inventory_health AS
WITH stock_summary AS (
    SELECT 
        ProductID,
        SUM(Quantity) AS current_stock_qty
    FROM production.productinventory
    GROUP BY ProductID
)
SELECT 
    pd.ProductID,
    pd.product_name,
    pd.category_name,
    pd.subcategory_name,
    pd.StandardCost,
    p.SafetyStockLevel,
    p.ReorderPoint,
    COALESCE(s.current_stock_qty, 0) AS current_stock_qty,
    (COALESCE(s.current_stock_qty, 0) * pd.StandardCost) AS inventory_valuation,
    CASE 
        WHEN COALESCE(s.current_stock_qty, 0) = 0 THEN 'Out of Stock'
        WHEN COALESCE(s.current_stock_qty, 0) <= p.SafetyStockLevel THEN 'Critical Stock Level'
        WHEN COALESCE(s.current_stock_qty, 0) <= p.ReorderPoint THEN 'Below Reorder Point'
        WHEN COALESCE(s.current_stock_qty, 0) > p.ReorderPoint * 3 THEN 'Overstocked'
        ELSE 'Healthy'
    END AS stock_status
FROM analytics.product_dim pd
INNER JOIN production.product p ON pd.ProductID = p.productid
LEFT JOIN stock_summary s ON pd.ProductID = s.ProductID;

-- View 13: Vendor Scorecard View (Purchasing / Vendor Analytics)
-- Computes vendor order volume, spend, average lead time, and defect rejection rates.
CREATE OR REPLACE VIEW analytics.vendor_scorecard AS
SELECT 
    VendorID,
    vendor_name,
    COUNT(DISTINCT PurchaseOrderID) AS purchase_orders_count,
    SUM(purchase_amount) AS total_purchase_spend,
    AVG(lead_time_days) AS avg_lead_time_days,
    SUM(ReceivedQty) AS total_qty_received,
    SUM(RejectedQty) AS total_qty_rejected,
    ROUND(
        CASE 
            WHEN SUM(ReceivedQty) > 0 THEN 
                (SUM(RejectedQty) / SUM(ReceivedQty)) * 100
            ELSE 0.0
        END, 
        2
    ) AS rejection_rate_pct,
    DENSE_RANK() OVER (ORDER BY SUM(purchase_amount) DESC) AS spend_rank
FROM analytics.purchasing_fact
GROUP BY VendorID, vendor_name;


-- ----------------------------------------------------------------------------
-- STAGE 4: EXECUTIVE LAYER (Unified Multi-Domain KPI Dashboard)
-- ----------------------------------------------------------------------------

-- View 14: Executive Dashboard KPIs View
-- Cross-joins monthly operational performance to provide a unified summary dashboard.
CREATE OR REPLACE VIEW analytics.executive_dashboard_kpis AS
WITH sales_kpi AS (
    SELECT 
        year,
        month,
        month_name,
        monthly_revenue,
        monthly_gross_profit,
        order_count,
        mom_revenue_growth_pct
    FROM analytics.monthly_revenue
),
customer_kpi AS (
    SELECT 
        COUNT(DISTINCT CustomerID) AS active_customers,
        ROUND(AVG(customer_lifetime_value), 2) AS avg_clv
    FROM analytics.customer_clv_segments
),
inventory_kpi AS (
    SELECT 
        SUM(inventory_valuation) AS total_inventory_value,
        SUM(CASE WHEN stock_status IN ('Out of Stock', 'Below Reorder Point', 'Critical Stock Level') THEN 1 ELSE 0 END) AS low_stock_product_count
    FROM analytics.inventory_health
),
purchasing_kpi AS (
    SELECT 
        SUM(total_purchase_spend) AS total_vendor_spend,
        AVG(avg_lead_time_days) AS avg_supplier_lead_time
    FROM analytics.vendor_scorecard
)
SELECT 
    s.year,
    s.month,
    s.month_name,
    s.monthly_revenue AS total_revenue,
    s.monthly_gross_profit AS total_gross_profit,
    s.order_count AS total_orders,
    s.mom_revenue_growth_pct,
    c.active_customers,
    c.avg_clv,
    i.total_inventory_value,
    i.low_stock_product_count,
    p.total_vendor_spend,
    ROUND(p.avg_supplier_lead_time, 2) AS avg_supplier_lead_time
FROM sales_kpi s
CROSS JOIN customer_kpi c
CROSS JOIN inventory_kpi i
CROSS JOIN purchasing_kpi p;
