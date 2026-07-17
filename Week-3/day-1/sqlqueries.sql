-- ============================================================
-- Week 3 Day 1 — SQL Foundations for Data Science
-- Dataset: Superstore Sales (9,994 rows)
-- Database: PostgreSQL 18 | Table: superstore_sales
-- ============================================================

-- ─────────────────────────────────────────────
-- SECTION 1: CREATE TABLE
-- ─────────────────────────────────────────────
CREATE TABLE superstore_sales (
    "Row ID"        INT PRIMARY KEY,
    "Order ID"      VARCHAR(30),
    "Order Date"    DATE,
    "Ship Date"     DATE,
    "Ship Mode"     VARCHAR(50),
    "Customer ID"   VARCHAR(30),
    "Customer Name" VARCHAR(100),
    "Segment"       VARCHAR(50),
    "Country"       VARCHAR(100),
    "City"          VARCHAR(100),
    "State"         VARCHAR(100),
    "Postal Code"   VARCHAR(20),
    "Region"        VARCHAR(50),
    "Product ID"    VARCHAR(30),
    "Category"      VARCHAR(50),
    "Sub-Category"  VARCHAR(50),
    "Product Name"  TEXT,
    "Sales"         NUMERIC(10,2),
    "Quantity"      INT,
    "Discount"      NUMERIC(4,2),
    "Profit"        NUMERIC(10,2)
);

-- ─────────────────────────────────────────────
-- SECTION 2: SELECT — retrieve all columns
-- ─────────────────────────────────────────────
SELECT *
FROM superstore_sales;

-- ─────────────────────────────────────────────
-- SECTION 3: LIMIT — preview first 10 rows
-- ─────────────────────────────────────────────
SELECT *
FROM superstore_sales
LIMIT 10;

-- ─────────────────────────────────────────────
-- SECTION 4: COUNT — total rows in table
-- ─────────────────────────────────────────────
SELECT COUNT(*)
FROM superstore_sales;

-- ─────────────────────────────────────────────
-- SECTION 5: information_schema — table structure
-- ─────────────────────────────────────────────
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'superstore_sales';

-- ─────────────────────────────────────────────
-- SECTION 6: DISTINCT — unique values
-- ─────────────────────────────────────────────
-- How many distinct categories exist?
SELECT DISTINCT "Category"
FROM superstore_sales;

-- Distinct shipping modes
SELECT DISTINCT "Ship Mode"
FROM superstore_sales;

-- Distinct regions
SELECT DISTINCT "Region"
FROM superstore_sales;

-- ─────────────────────────────────────────────
-- SECTION 7: WHERE — filter rows
-- ─────────────────────────────────────────────
-- Orders from the West region only
SELECT "Order ID", "Customer Name", "Region", "Sales"
FROM superstore_sales
WHERE "Region" = 'West';

-- Orders with Sales greater than $1,000
SELECT "Order ID", "Product Name", "Sales"
FROM superstore_sales
WHERE "Sales" > 1000;

-- Orders from Technology category with a discount applied
SELECT "Order ID", "Category", "Sales", "Discount"
FROM superstore_sales
WHERE "Category" = 'Technology'
  AND "Discount" > 0;

-- ─────────────────────────────────────────────
-- SECTION 8: ORDER BY — sort results
-- ─────────────────────────────────────────────
-- Top 10 highest-revenue orders
SELECT "Order ID", "Product Name", "Sales"
FROM superstore_sales
ORDER BY "Sales" DESC
LIMIT 10;

-- 10 most recent orders
SELECT "Order ID", "Order Date", "Customer Name", "Sales"
FROM superstore_sales
ORDER BY "Order Date" DESC
LIMIT 10;

-- Orders sorted by region then by sales descending
SELECT "Region", "Order ID", "Sales"
FROM superstore_sales
ORDER BY "Region" ASC, "Sales" DESC
LIMIT 20;

-- ─────────────────────────────────────────────
-- SECTION 9: Aliases (AS)
-- ─────────────────────────────────────────────
-- Rename columns for clarity in output
SELECT
    "Customer Name"  AS customer,
    "Region"         AS region,
    "Sales"          AS revenue,
    "Profit"         AS profit,
    "Discount"       AS discount_rate
FROM superstore_sales
ORDER BY revenue DESC
LIMIT 10;

-- ─────────────────────────────────────────────
-- SECTION 10: Aggregate Functions
-- COUNT, SUM, AVG, MIN, MAX
-- ─────────────────────────────────────────────
-- Overall summary statistics
SELECT
    COUNT(*)                    AS total_orders,
    ROUND(SUM("Sales"), 2)      AS total_revenue,
    ROUND(AVG("Sales"), 2)      AS avg_order_value,
    ROUND(MIN("Sales"), 2)      AS min_sale,
    ROUND(MAX("Sales"), 2)      AS max_sale,
    ROUND(SUM("Profit"), 2)     AS total_profit,
    ROUND(AVG("Profit"), 2)     AS avg_profit
FROM superstore_sales;

-- ─────────────────────────────────────────────
-- SECTION 11: GROUP BY — aggregate by category
-- ─────────────────────────────────────────────
-- Total sales and profit by Category
SELECT
    "Category",
    COUNT(*)                    AS num_orders,
    ROUND(SUM("Sales"), 2)      AS total_sales,
    ROUND(AVG("Sales"), 2)      AS avg_sales,
    ROUND(SUM("Profit"), 2)     AS total_profit
FROM superstore_sales
GROUP BY "Category"
ORDER BY total_sales DESC;

-- Sales and profit by Region
SELECT
    "Region",
    COUNT(*)                    AS num_orders,
    ROUND(SUM("Sales"), 2)      AS total_sales,
    ROUND(SUM("Profit"), 2)     AS total_profit,
    ROUND(AVG("Discount"), 4)   AS avg_discount
FROM superstore_sales
GROUP BY "Region"
ORDER BY total_profit DESC;

-- Top 5 Sub-Categories by total profit
SELECT
    "Sub-Category",
    COUNT(*)                    AS num_orders,
    ROUND(SUM("Profit"), 2)     AS total_profit
FROM superstore_sales
GROUP BY "Sub-Category"
ORDER BY total_profit DESC
LIMIT 5;

-- ─────────────────────────────────────────────
-- SECTION 12: WHERE vs HAVING
-- ─────────────────────────────────────────────
-- WHERE filters rows before grouping
-- HAVING filters groups after aggregation

-- Regions where average discount is more than 15%
SELECT
    "Region",
    ROUND(AVG("Discount"), 4) AS avg_discount,
    COUNT(*)                  AS num_orders
FROM superstore_sales
WHERE "Category" = 'Furniture'         -- filter rows first (WHERE)
GROUP BY "Region"
HAVING AVG("Discount") > 0.15          -- then filter groups (HAVING)
ORDER BY avg_discount DESC;

-- Sub-categories with total sales over $100,000
SELECT
    "Sub-Category",
    ROUND(SUM("Sales"), 2) AS total_sales
FROM superstore_sales
GROUP BY "Sub-Category"
HAVING SUM("Sales") > 100000
ORDER BY total_sales DESC;
