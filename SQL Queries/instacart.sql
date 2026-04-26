-- =========================================
-- Instacart Staging Layer (PostgreSQL)
-- =========================================

-- 1) Create staging tables (idempotent)
CREATE TABLE IF NOT EXISTS stg_orders (
    order_id INT,
    user_id INT,
    eval_set VARCHAR(10),
    order_number INT,
    order_dow INT,
    order_hour_of_day INT,
    days_since_prior_order NUMERIC
);

CREATE TABLE IF NOT EXISTS stg_products (
    product_id INT,
    product_name TEXT,
    aisle_id INT,
    department_id INT
);

CREATE TABLE IF NOT EXISTS stg_order_products_prior (
    order_id INT,
    product_id INT,
    add_to_cart_order INT,
    reordered INT
);

CREATE TABLE IF NOT EXISTS stg_order_products_train (
    order_id INT,
    product_id INT,
    add_to_cart_order INT,
    reordered INT
);

CREATE TABLE IF NOT EXISTS stg_aisles (
    aisle_id INT,
    aisle TEXT
);

CREATE TABLE IF NOT EXISTS stg_departments (
    department_id INT,
    department TEXT
);

-- 2) Quick profiling
SELECT MAX(days_since_prior_order) AS max_days_since_prior_order
FROM stg_orders;

SELECT * FROM stg_products ORDER BY RANDOM() LIMIT 5;
SELECT * FROM stg_departments LIMIT 5;
SELECT * FROM stg_order_products_prior LIMIT 5;
SELECT * FROM stg_order_products_train LIMIT 5;
SELECT * FROM stg_aisles LIMIT 5;

-- 3) Row counts
SELECT
    (SELECT COUNT(*) FROM stg_orders) AS orders_count,
    (SELECT COUNT(*) FROM stg_products) AS products_count,
    (SELECT COUNT(*) FROM stg_departments) AS departments_count,
    (SELECT COUNT(*) FROM stg_order_products_prior) AS prior_products_count,
    (SELECT COUNT(*) FROM stg_order_products_train) AS train_products_count,
    (SELECT COUNT(*) FROM stg_aisles) AS aisles_count;

SELECT 'orders' AS table_name, COUNT(*) AS row_count FROM stg_orders
UNION ALL
SELECT 'products', COUNT(*) FROM stg_products
UNION ALL
SELECT 'order_products_prior', COUNT(*) FROM stg_order_products_prior
UNION ALL
SELECT 'order_products_train', COUNT(*) FROM stg_order_products_train
UNION ALL
SELECT 'aisles', COUNT(*) FROM stg_aisles
UNION ALL
SELECT 'departments', COUNT(*) FROM stg_departments;

-- 4) Data checks
SELECT user_id, eval_set
FROM stg_orders
WHERE user_id = 52980;

SELECT COUNT(*) AS matched_or_unmatched_rows
FROM stg_order_products_prior op
FULL OUTER JOIN stg_orders o ON op.order_id = o.order_id;

SELECT reordered
FROM stg_order_products_train
ORDER BY reordered DESC
LIMIT 3;

-- Top users by reordered items in train
SELECT
    o.user_id,
    SUM(op.reordered) AS total_reordered_items
FROM stg_orders o
JOIN stg_order_products_train op ON o.order_id = op.order_id
GROUP BY o.user_id
ORDER BY total_reordered_items DESC
LIMIT 3;

-- Top users by reordered items in prior
SELECT
    o.user_id,
    SUM(op.reordered) AS total_reordered_items
FROM stg_orders o
JOIN stg_order_products_prior op ON o.order_id = op.order_id
GROUP BY o.user_id
ORDER BY total_reordered_items DESC
LIMIT 3;

-- User-order-product story sample
SELECT
    o.user_id,
    o.order_id,
    p.product_name,
    a.aisle,
    d.department
FROM stg_order_products_prior op
JOIN stg_orders o ON op.order_id = o.order_id
JOIN stg_products p ON op.product_id = p.product_id
JOIN stg_aisles a ON p.aisle_id = a.aisle_id
JOIN stg_departments d ON p.department_id = d.department_id
LIMIT 20;

-- Column info
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'stg_aisles'
ORDER BY ordinal_position;

-- NULL checks
SELECT
    COUNT(*) - COUNT(product_id) AS product_id_nulls,
    COUNT(*) - COUNT(product_name) AS product_name_nulls,
    COUNT(*) - COUNT(aisle_id) AS aisle_id_nulls,
    COUNT(*) - COUNT(department_id) AS department_id_nulls
FROM stg_products;

SELECT
    COUNT(*) AS total_rows,
    COUNT(*) - COUNT(aisle_id) AS aisle_id_nulls,
    COUNT(*) - COUNT(aisle) AS aisle_name_nulls
FROM stg_aisles;

-- Duplicate detection in prior lines
WITH ranked_orders AS (
    SELECT
        order_id,
        product_id,
        add_to_cart_order,
        reordered,
        ROW_NUMBER() OVER (PARTITION BY order_id, product_id ORDER BY add_to_cart_order) AS row_num
    FROM stg_order_products_prior
)
SELECT *
FROM ranked_orders
WHERE row_num > 1;

-- Reordered value distribution
SELECT
    reordered,
    COUNT(*) AS row_count
FROM stg_order_products_prior
GROUP BY reordered
ORDER BY row_count DESC;