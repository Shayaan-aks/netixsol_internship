# 🏢 AdventureWorks Enterprise Analytics Layer
### Week 3 – Friday Hackathon Submission

---

## 📌 Project Overview

This project implements a **reusable Analytics Layer** on top of the AdventureWorks enterprise database. Instead of querying raw operational tables directly in reporting tools, we designed an intermediate `analytics` schema that transforms raw transactional data into clean, pre-aggregated, business-ready datasets.

The final deliverable includes:
- A **chained SQL pipeline** (`analytics_pipeline.sql`) with 14 analytical views
- An **Executive Analytics Notebook** (`executive_analysis.ipynb`) with 8 visualizations, insights, and recommendations

---

## 🗄️ Database Overview

**Database:** `adventureworks` (PostgreSQL 18)  
**Source Dataset:** AdventureWorks for PostgreSQL — a comprehensive enterprise database modelling a bicycle manufacturing company.

| Schema | Description | Tables |
|--------|-------------|--------|
| `person` | Contacts, addresses, person details | 13 tables |
| `humanresources` | Employees, departments, payroll | 6 tables |
| `production` | Products, inventory, manufacturing | 25 tables |
| `purchasing` | Vendors, purchase orders | 5 tables |
| `sales` | Customers, orders, sales territories | 19 tables |
| **`analytics`** | **Our analytics layer (this project)** | **14 views** |

---

## 🏗️ Analytics Architecture

```
Raw Operational Schemas (68 tables across 5 schemas)
        │
        ▼
┌─────────────────────────────────────────┐
│          DIMENSIONAL LAYER              │
│  calendar_dim  │  product_dim           │
│  customer_dim  │  sales_person_dim      │
└─────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│              FACT LAYER                 │
│     sales_fact  │  purchasing_fact      │
└─────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│         ANALYTICS/AGGREGATION LAYER     │
│  monthly_revenue    │  customer_clv_segments  │
│  product_profitability  │  territory_sales    │
│  salesperson_performance │ inventory_health   │
│  vendor_scorecard                             │
└─────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│         EXECUTIVE LAYER                 │
│      executive_dashboard_kpis           │
└─────────────────────────────────────────┘
        │
        ▼
  executive_analysis.ipynb
  (Reads ONLY from analytics.* schema)
```

---

## 📊 Intermediate Tables / Views Created

| # | View Name | Stage | Description |
|---|-----------|-------|-------------|
| 1 | `analytics.calendar_dim` | Dimensional | Date dimension mapping every date to Year, Quarter, Month, Day, Weekend flag |
| 2 | `analytics.product_dim` | Dimensional | Products enriched with subcategory, category, markup %, and status |
| 3 | `analytics.customer_dim` | Dimensional | Customers with individual/store name, territory, and customer type |
| 4 | `analytics.sales_person_dim` | Dimensional | Salesperson details with employee info, quota, commission rate |
| 5 | `analytics.sales_fact` | Fact | Flat sales line table with discount-adjusted revenue, COGS, profit, and proportionally allocated tax/freight |
| 6 | `analytics.purchasing_fact` | Fact | Purchase order lines with lead time, quantities, rejection data |
| 7 | `analytics.monthly_revenue` | Analytics | Monthly aggregated revenue, gross profit, order count, and MoM growth using `LAG()` |
| 8 | `analytics.customer_clv_segments` | Analytics | Customer CLV, recency, frequency, RFM scoring with `NTILE(5)`, and segment classification |
| 9 | `analytics.product_profitability` | Analytics | Product-level revenue, COGS, profit, margin, and `DENSE_RANK()` within category |
| 10 | `analytics.territory_sales` | Analytics | Territory revenue totals, rankings, and percentage contribution |
| 11 | `analytics.salesperson_performance` | Analytics | Actual vs. quota comparison, commission earned, and sales ranking |
| 12 | `analytics.inventory_health` | Analytics | Current stock vs. safety levels with health status flags |
| 13 | `analytics.vendor_scorecard` | Analytics | Vendor spend, lead time, rejection rate, and spend ranking |
| 14 | `analytics.executive_dashboard_kpis` | Executive | Monthly cross-domain KPI table joining sales, customer, inventory, and vendor metrics |

---

## 🔧 SQL Design Decisions

### 1. Why Views Instead of Tables?
Views were chosen over materialized tables for flexibility — they always reflect the latest operational data without requiring refresh jobs. In a production environment, frequently-used views would be materialized and refreshed nightly.

### 2. Chained Dependencies
Every analytics view builds on the dimensional or fact views below it. This means:
- COGS is calculated once in `sales_fact` and reused in `product_profitability`
- Calendar dates are resolved once in `calendar_dim` and reused in `monthly_revenue`

### 3. Window Functions Used
- `LAG()` — Month-over-Month revenue comparison
- `NTILE(5)` — RFM segmentation into 5 equal quintile buckets
- `DENSE_RANK()` — Ranking products within categories and salespeople by revenue
- `SUM() OVER ()` — Revenue contribution percentages in territory analysis

### 4. No Raw Table Queries in Notebook
The Jupyter notebook queries **zero raw operational tables** — all analysis comes from the `analytics.*` schema, enforcing the analytics layer contract.

---

## ▶️ Execution Instructions

### Step 1: Set up the AdventureWorks database
```bash
# Create the database
psql -U postgres -c "CREATE DATABASE adventureworks;"

# Load schema and data from the dataset directory
psql -U postgres -d adventureworks -f install.sql
```

### Step 2: Run the Analytics Pipeline
```bash
psql -U postgres -d adventureworks -f analytics_pipeline.sql
```

### Step 3: Install Python dependencies
```bash
pip install pandas sqlalchemy psycopg2-binary matplotlib seaborn numpy
```

### Step 4: Open the Jupyter Notebook
```bash
jupyter notebook executive_analysis.ipynb
```

Update the DB credentials in Cell 1 if needed, then **Run All Cells**.

---

## 📁 Project Structure

```
enterprise_analytics_hackathon/
│
├── README.md                    ← This file
│
├── analytics_pipeline.sql       ← All SQL (14 views, fully commented)
│
├── executive_analysis.ipynb     ← Jupyter Notebook with analysis & recommendations
│
├── charts/                      ← Auto-generated visualization PNG files
│   ├── 1_revenue_trend.png
│   ├── 2_sales_by_territory.png
│   ├── 3_customer_segments.png
│   ├── 4_product_performance.png
│   ├── 5_category_revenue.png
│   ├── 6_employee_performance.png
│   ├── 7_inventory_status.png
│   └── 8_executive_kpi_summary.png
│
├── screenshots/                 ← pgAdmin / query execution screenshots
│
└── documentation/               ← Additional design docs (optional)
```

---

## ⚙️ Challenges Faced

1. **Column name casing** — PostgreSQL lowercases all unquoted column names. Fixed by explicitly using lowercase names in Python DataFrame queries.
2. **Proportional Tax/Freight Allocation** — SalesOrderHeader stores total tax/freight at the order level. We allocated it to each line item proportionally by line subtotal share.
3. **HierarchyID columns** — The `install.sql` for PostgreSQL performs a complex binary-to-path conversion for Employee org chart data. This required understanding the transformation before querying.
4. **Missing subcategory** — Some products (raw materials/components) have no subcategory or category. These are handled with `LEFT JOIN` and shown as NULL in analytics views.

---

## 📌 Assumptions Made

1. `StandardCost` is used as the cost basis for gross profit calculations.
2. The `SalesQuota` in `sales.salesperson` is treated as the annual quota target.
3. Customers with both `PersonID` and `StoreID` are classified as "Store Contact."
4. For RFM segmentation, a 5-bucket NTILE is used for Recency, Frequency, and Monetary independently.
5. "Repeat Customers" are defined as customers with more than 1 distinct order.

---

*Submitted by: Shayaan | Week 3 – Friday Hackathon | Netixsol Internship Program*
