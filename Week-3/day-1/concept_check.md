# Week 3 Day 1 — Concept Check

**Dataset:** Superstore Sales Dataset (Kaggle)  
**Database:** PostgreSQL 18 | **Table:** `superstore_sales` | **Rows:** 9,994

---

## Q1. What problem does SQL solve that CSV files cannot?

CSV files are flat text files — they have **no query engine**. To filter, aggregate,
or join CSV data you must load the entire file into memory (Python, Excel, etc.).  
SQL solves this by storing data in a **relational database with an optimised engine**
that can:

- Filter, sort, and aggregate **millions of rows without loading them into RAM**
- Handle **concurrent reads and writes** from multiple users simultaneously
- Enforce **data integrity** via constraints (PRIMARY KEY, FOREIGN KEY, NOT NULL)
- Execute **complex multi-table JOINs** efficiently with indexes
- Provide **ACID transactions** — changes are atomic and durable

> A CSV with 50 million rows would crash Excel and slow Pandas; PostgreSQL handles
> it in milliseconds with proper indexing.

---

## Q2. What is the difference between a database table and a spreadsheet?

| Aspect | Database Table | Spreadsheet |
|---|---|---|
| **Schema enforcement** | Strict — each column has a fixed data type | Loose — any cell can hold any value |
| **Scalability** | Millions of rows with constant-time queries | Degrades above ~1 million rows |
| **Concurrency** | Multiple users read/write simultaneously | Single-user file locking |
| **Data integrity** | PRIMARY KEY, FOREIGN KEY, CHECK constraints | No built-in constraint system |
| **Querying** | SQL — declarative, powerful | Formulas — procedural, limited |
| **Relationships** | Can JOIN multiple tables | Must manually vlookup/merge |
| **Storage** | Optimised binary format on disk | Human-readable but large files |

---

## Q3. What is a Primary Key?

A **Primary Key** is a column (or combination of columns) that **uniquely identifies
every row** in a table. Rules:

- Must be **unique** — no two rows can share the same value
- Must be **NOT NULL** — every row must have a value
- Each table can have **only one** primary key
- PostgreSQL automatically creates a **unique index** on the primary key for fast lookups

**Example in our table:**
```sql
"Row ID" INT PRIMARY KEY
```
`Row ID` uniquely identifies each sale record. No two sales share the same Row ID.

---

## Q4. What is a Foreign Key?

A **Foreign Key** is a column in one table that **references the Primary Key of
another table**, establishing a relationship between tables.

- Enforces **referential integrity** — you cannot insert a value that doesn't exist
  in the referenced table
- Prevents **orphan records** — you cannot delete a parent row if child rows reference it

**Example:**
```sql
-- Orders table
CREATE TABLE orders (
    order_id  VARCHAR(30) PRIMARY KEY,
    customer_id VARCHAR(30) REFERENCES customers(customer_id)
);
```
Here `customer_id` in `orders` is a Foreign Key pointing to `customers.customer_id`.

In our Superstore dataset everything is in one table; in a normalised design
`Customer ID`, `Product ID`, and `Order ID` would each live in separate tables
linked by foreign keys.

---

## Q5. What is the difference between WHERE and HAVING?

| Clause | Filters | Timing | Can use aggregates? |
|---|---|---|---|
| `WHERE` | Individual **rows** | **Before** GROUP BY (pre-aggregation) | ❌ No |
| `HAVING` | **Groups** of rows | **After** GROUP BY (post-aggregation) | ✅ Yes |

**Example:**
```sql
-- WHERE filters rows before grouping
SELECT "Region", COUNT(*) AS order_count
FROM superstore_sales
WHERE "Sales" > 100          -- only rows where Sales > 100
GROUP BY "Region"
HAVING COUNT(*) > 200;       -- only regions with more than 200 qualifying orders
```

> Rule of thumb: if your filter involves an **aggregate function** (`COUNT`, `SUM`,
> `AVG` …), use `HAVING`. Otherwise use `WHERE`.

---

## Q6. What is the difference between ORDER BY and GROUP BY?

| Clause | Purpose | Output |
|---|---|---|
| `ORDER BY` | **Sorts** the result rows by one or more columns | Same number of rows, different order |
| `GROUP BY` | **Collapses** rows that share a value into one group | Fewer rows — one per unique group value |

**Example:**
```sql
-- ORDER BY: all 9,994 rows, sorted by Sales descending
SELECT "Order ID", "Sales"
FROM superstore_sales
ORDER BY "Sales" DESC;

-- GROUP BY: 4 rows — one per region with total sales
SELECT "Region", SUM("Sales") AS total_sales
FROM superstore_sales
GROUP BY "Region"
ORDER BY total_sales DESC;
```

---

## Q7. What does DISTINCT do?

`DISTINCT` **removes duplicate rows** from the result set, returning only unique
combinations of the selected columns.

```sql
-- Without DISTINCT: returns all 9,994 rows (many repeated categories)
SELECT "Category" FROM superstore_sales;

-- With DISTINCT: returns only 3 rows (Furniture, Office Supplies, Technology)
SELECT DISTINCT "Category" FROM superstore_sales;
```

Use cases:
- Find all unique values in a column
- Check how many distinct customers / products / regions exist
- De-duplicate before further processing

---

## Q8. When should you use LIMIT?

`LIMIT` restricts the number of rows returned. Use it when:

1. **Exploring a new table** — `SELECT * FROM table LIMIT 10` to preview structure
2. **Prototyping queries** — test logic on a small sample before running on all rows
3. **Pagination** — fetch pages of results (combined with `OFFSET`)
4. **Top-N queries** — find the top 5 most profitable products

```sql
-- Preview the first 10 rows
SELECT * FROM superstore_sales LIMIT 10;

-- Top 5 most profitable orders
SELECT "Order ID", "Profit"
FROM superstore_sales
ORDER BY "Profit" DESC
LIMIT 5;
```

> Always combine `LIMIT` with `ORDER BY` for deterministic Top-N results;
> without `ORDER BY` the rows returned are arbitrary.

---

## Q9. What are aggregate functions?

Aggregate functions **compute a single summary value from multiple rows**. They
are used with `SELECT` (and optionally `GROUP BY`).

| Function | Description | Example |
|---|---|---|
| `COUNT(*)` | Total number of rows | `SELECT COUNT(*) FROM superstore_sales;` → 9994 |
| `COUNT(col)` | Rows where column is NOT NULL | `SELECT COUNT("Postal Code") FROM superstore_sales;` |
| `SUM(col)` | Total of numeric column | `SELECT SUM("Sales") FROM superstore_sales;` |
| `AVG(col)` | Arithmetic mean | `SELECT AVG("Profit") FROM superstore_sales;` |
| `MIN(col)` | Smallest value | `SELECT MIN("Sales") FROM superstore_sales;` |
| `MAX(col)` | Largest value | `SELECT MAX("Sales") FROM superstore_sales;` |

All aggregate functions **ignore NULL values** (except `COUNT(*)`).

---

## Q10. Why do Data Scientists prefer databases over Excel for large datasets?

| Concern | Excel | PostgreSQL Database |
|---|---|---|
| **Row limit** | ~1 million rows hard cap | Billions of rows (no practical limit) |
| **Memory** | Loads entire file into RAM | Reads only what the query needs |
| **Speed** | Slow on >100K rows | Millisecond queries with indexes |
| **Reproducibility** | Formulas break; manual steps | SQL queries are version-controllable |
| **Collaboration** | File locking, merge conflicts | Multiple concurrent users |
| **Automation** | VBA macros, fragile | SQL scripts run in pipelines (Airflow, etc.) |
| **Data integrity** | Any cell can contain anything | Schema + constraints enforce correctness |
| **Integration** | Manual export/import | Direct connections from Python, R, Tableau |

> For a Data Scientist, SQL also enables **exploratory analysis at the source** —
> aggregating and filtering before pulling data into Pandas reduces memory usage
> and speeds up iteration significantly.
