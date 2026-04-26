-- =========================================
-- Materialized Views and Aggregations (PostgreSQL)
-- =========================================

-- Drop in reverse dependency/usage order for safe re-runs
DROP MATERIALIZED VIEW IF EXISTS mv_reorder_time_v2;
DROP MATERIALIZED VIEW IF EXISTS mv_orders_time_v2;
DROP MATERIALIZED VIEW IF EXISTS mv_basket_analysis_v2;
DROP MATERIALIZED VIEW IF EXISTS mv_reorder_department_v2;
DROP MATERIALIZED VIEW IF EXISTS mv_reorder_product_v2;
DROP MATERIALIZED VIEW IF EXISTS mv_department_performance_v2;
DROP MATERIALIZED VIEW IF EXISTS mv_product_performance_v2;
DROP MATERIALIZED VIEW IF EXISTS mv_overview_kpis_v2;

-- 1) Overview dashboard
CREATE MATERIALIZED VIEW mv_overview_kpis_v2 AS
SELECT
    COUNT(DISTINCT f.order_id) AS total_orders,
    COUNT(DISTINCT o.user_id) AS total_users,
    COUNT(DISTINCT f.product_id) AS total_products,
    ROUND(SUM(f.reordered)::NUMERIC / NULLIF(COUNT(*), 0), 4) AS overall_reorder_rate
FROM fact_order_products f
JOIN dim_orders o ON f.order_id = o.order_id;

-- 2) Product performance
CREATE MATERIALIZED VIEW mv_product_performance_v2 AS
SELECT
    f.product_id,
    p.product_name,
    COUNT(*) AS total_orders
FROM fact_order_products f
JOIN dim_products p ON f.product_id = p.product_id
GROUP BY f.product_id, p.product_name;

-- 3) Department performance
CREATE MATERIALIZED VIEW mv_department_performance_v2 AS
SELECT
    d.department_id,
    d.department,
    COUNT(*) AS total_orders
FROM fact_order_products f
JOIN dim_products p ON f.product_id = p.product_id
JOIN dim_departments d ON p.department_id = d.department_id
GROUP BY d.department_id, d.department;

-- 4) Reorder analysis by product and department
CREATE MATERIALIZED VIEW mv_reorder_product_v2 AS
WITH agg AS (
    SELECT
        product_id,
        COUNT(*) AS total_orders,
        SUM(reordered) AS reorder_count
    FROM fact_order_products
    GROUP BY product_id
)
SELECT
    a.product_id,
    p.product_name,
    a.total_orders,
    a.reorder_count,
    ROUND(a.reorder_count::NUMERIC / NULLIF(a.total_orders, 0), 4) AS reorder_rate
FROM agg a
JOIN dim_products p ON a.product_id = p.product_id;

CREATE MATERIALIZED VIEW mv_reorder_department_v2 AS
SELECT
    d.department_id,
    d.department,
    COUNT(*) AS total_orders,
    SUM(f.reordered) AS reorder_count,
    ROUND(SUM(f.reordered)::NUMERIC / NULLIF(COUNT(*), 0), 4) AS reorder_rate
FROM fact_order_products f
JOIN dim_products p ON f.product_id = p.product_id
JOIN dim_departments d ON p.department_id = d.department_id
GROUP BY d.department_id, d.department;

-- 5) Basket analysis
CREATE MATERIALIZED VIEW mv_basket_analysis_v2 AS
SELECT
    f.order_id,
    COUNT(f.product_id) AS basket_size
FROM fact_order_products f
GROUP BY f.order_id;

-- 6) Time analysis
CREATE MATERIALIZED VIEW mv_orders_time_v2 AS
SELECT
    o.order_hour_of_day,
    COUNT(DISTINCT f.order_id) AS total_orders
FROM fact_order_products f
JOIN dim_orders o ON f.order_id = o.order_id
GROUP BY o.order_hour_of_day;

CREATE MATERIALIZED VIEW mv_reorder_time_v2 AS
SELECT
    o.order_hour_of_day,
    COUNT(*) AS total_orders,
    SUM(f.reordered) AS reorder_count,
    ROUND(SUM(f.reordered)::NUMERIC / NULLIF(COUNT(*), 0), 4) AS reorder_rate
FROM fact_order_products f
JOIN dim_orders o ON f.order_id = o.order_id
GROUP BY o.order_hour_of_day;

-- 7) Indexes on materialized views
DROP INDEX IF EXISTS idx_mv_product_perf_pid;
DROP INDEX IF EXISTS idx_mv_department_perf_dept;
DROP INDEX IF EXISTS idx_mv_reorder_product_pid;
DROP INDEX IF EXISTS idx_mv_reorder_department_dept;
DROP INDEX IF EXISTS idx_mv_basket_order;
DROP INDEX IF EXISTS idx_mv_orders_time_hour;
DROP INDEX IF EXISTS idx_mv_reorder_time_hour;

CREATE INDEX idx_mv_product_perf_pid
ON mv_product_performance_v2 (product_id);

CREATE INDEX idx_mv_department_perf_dept
ON mv_department_performance_v2 (department_id);

CREATE INDEX idx_mv_reorder_product_pid
ON mv_reorder_product_v2 (product_id);

CREATE INDEX idx_mv_reorder_department_dept
ON mv_reorder_department_v2 (department_id);

CREATE INDEX idx_mv_basket_order
ON mv_basket_analysis_v2 (order_id);

CREATE INDEX idx_mv_orders_time_hour
ON mv_orders_time_v2 (order_hour_of_day);

CREATE INDEX idx_mv_reorder_time_hour
ON mv_reorder_time_v2 (order_hour_of_day);

-- 8) Validation and QA
SELECT * FROM mv_overview_kpis_v2;

SELECT *
FROM mv_product_performance_v2
ORDER BY total_orders DESC
LIMIT 10;

SELECT *
FROM mv_department_performance_v2
ORDER BY total_orders DESC;

SELECT *
FROM mv_reorder_product_v2
ORDER BY reorder_rate DESC
LIMIT 10;

SELECT *
FROM mv_reorder_department_v2
ORDER BY reorder_rate DESC;

SELECT
    basket_size,
    COUNT(*) AS order_count
FROM mv_basket_analysis_v2
GROUP BY basket_size
ORDER BY basket_size;

SELECT *
FROM mv_orders_time_v2
ORDER BY order_hour_of_day;

SELECT *
FROM mv_reorder_time_v2
ORDER BY order_hour_of_day;

-- Data quality checks
SELECT COUNT(*) AS null_product_id_rows
FROM mv_product_performance_v2
WHERE product_id IS NULL;

SELECT COUNT(*) AS null_department_id_rows
FROM mv_department_performance_v2
WHERE department_id IS NULL;

SELECT *
FROM mv_reorder_product_v2
WHERE reorder_rate < 0 OR reorder_rate > 1;

SELECT product_id, COUNT(*) AS duplicate_count
FROM mv_product_performance_v2
GROUP BY product_id
HAVING COUNT(*) > 1;

