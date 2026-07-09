CREATE TABLE superstore_sales (
    "Row ID" INT PRIMARY KEY,
    "Order ID" VARCHAR(30),
    "Order Date" TEXT,
    "Ship Date" TEXT,
    "Ship Mode" VARCHAR(50),
    "Customer ID" VARCHAR(30),
    "Customer Name" VARCHAR(100),
    "Segment" VARCHAR(50),
    "Country" VARCHAR(100),
    "City" VARCHAR(100),
    "State" VARCHAR(100),
    "Postal Code" VARCHAR(20),
    "Region" VARCHAR(50),
    "Product ID" VARCHAR(30),
    "Category" VARCHAR(50),
    "Sub-Category" VARCHAR(50),
    "Product Name" TEXT,
    "Sales" NUMERIC(10,2),
    "Quantity" INT,
    "Discount" NUMERIC(4,2),
    "Profit" NUMERIC(10,2)
);

SELECT *
FROM superstore_sales;

SELECT COUNT(*)
FROM superstore_sales;

SELECT
column_name,
data_type
FROM information_schema.columns
WHERE table_name='superstore_sales';
