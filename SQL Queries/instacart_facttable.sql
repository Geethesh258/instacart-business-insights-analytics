-- =========================================
-- Instacart Dimensional Model (PostgreSQL)
-- =========================================

-- Rebuild in dependency order for repeatable execution
DROP TABLE IF EXISTS fact_order_products;
DROP TABLE IF EXISTS dim_products;
DROP TABLE IF EXISTS dim_orders;
DROP TABLE IF EXISTS dim_aisles;
DROP TABLE IF EXISTS dim_departments;

-- 1) Dimensions
CREATE TABLE dim_orders AS
SELECT
    order_id,
    user_id,
    order_number,
    order_dow,
    order_hour_of_day,
    days_since_prior_order
FROM stg_orders;

CREATE TABLE dim_products AS
SELECT
    product_id,
    product_name,
    aisle_id,
    department_id
FROM stg_products;

CREATE TABLE dim_aisles AS
SELECT
    aisle_id,
    aisle
FROM stg_aisles;

CREATE TABLE dim_departments AS
SELECT
    department_id,
    department
FROM stg_departments;

-- 2) Fact
CREATE TABLE fact_order_products AS
SELECT
    op.order_id,
    op.product_id,
    op.add_to_cart_order,
    op.reordered
FROM stg_order_products_prior op;

-- 3) Keys and relationships
ALTER TABLE dim_orders ADD PRIMARY KEY (order_id);
ALTER TABLE dim_products ADD PRIMARY KEY (product_id);
ALTER TABLE dim_aisles ADD PRIMARY KEY (aisle_id);
ALTER TABLE dim_departments ADD PRIMARY KEY (department_id);

ALTER TABLE fact_order_products
ADD PRIMARY KEY (order_id, product_id);

ALTER TABLE fact_order_products
ADD CONSTRAINT fk_fact_order
FOREIGN KEY (order_id) REFERENCES dim_orders(order_id);

ALTER TABLE fact_order_products
ADD CONSTRAINT fk_fact_product
FOREIGN KEY (product_id) REFERENCES dim_products(product_id);

ALTER TABLE dim_products
ADD CONSTRAINT fk_dim_products_aisle
FOREIGN KEY (aisle_id) REFERENCES dim_aisles(aisle_id);

ALTER TABLE dim_products
ADD CONSTRAINT fk_dim_products_department
FOREIGN KEY (department_id) REFERENCES dim_departments(department_id);

-- 4) Indexes
CREATE INDEX idx_fact_order_products_order_id ON fact_order_products(order_id);
CREATE INDEX idx_fact_order_products_product_id ON fact_order_products(product_id);
CREATE INDEX idx_dim_products_department_id ON dim_products(department_id);
CREATE INDEX idx_dim_products_aisle_id ON dim_products(aisle_id);

-- 5) Validation
SELECT COUNT(*) AS fact_rows
FROM fact_order_products;

SELECT COUNT(*) AS fact_rows_with_matching_product
FROM fact_order_products f
JOIN dim_products p ON f.product_id = p.product_id;