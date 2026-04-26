-- =========================================
-- Views and Aggregations (PostgreSQL)
-- =========================================

-- Recreate all materialized views so this script is repeatable
DROP MATERIALIZED VIEW IF EXISTS mv_top_products;
DROP MATERIALIZED VIEW IF EXISTS mv_department_sales;
DROP MATERIALIZED VIEW IF EXISTS mv_reorder_rate;
DROP MATERIALIZED VIEW IF EXISTS mv_orders_by_hour;
DROP MATERIALIZED VIEW IF EXISTS mv_basket_size;

CREATE MATERIALIZED VIEW mv_top_products AS
SELECT
	p.product_id,
	p.product_name,
	COUNT(*) AS total_orders
FROM fact_order_products f
JOIN dim_products p ON f.product_id = p.product_id
GROUP BY p.product_id, p.product_name;

CREATE MATERIALIZED VIEW mv_department_sales AS
SELECT
	d.department_id,
	d.department,
	COUNT(*) AS total_orders
FROM fact_order_products f
JOIN dim_products p ON f.product_id = p.product_id
JOIN dim_departments d ON p.department_id = d.department_id
GROUP BY d.department_id, d.department;

CREATE MATERIALIZED VIEW mv_reorder_rate AS
SELECT
	reordered,
	COUNT(*) AS total_count,
	ROUND(COUNT(*) * 100.0 / NULLIF(SUM(COUNT(*)) OVER (), 0), 2) AS reorder_rate_pct
FROM fact_order_products
GROUP BY reordered;

CREATE MATERIALIZED VIEW mv_orders_by_hour AS
SELECT
	order_hour_of_day,
	COUNT(*) AS total_orders
FROM dim_orders
GROUP BY order_hour_of_day;

CREATE MATERIALIZED VIEW mv_basket_size AS
SELECT
	order_id,
	COUNT(product_id) AS basket_size
FROM fact_order_products
GROUP BY order_id;

DROP INDEX IF EXISTS idx_mv_top_products;
DROP INDEX IF EXISTS idx_mv_department_sales;

CREATE INDEX idx_mv_top_products ON mv_top_products(product_id);
CREATE INDEX idx_mv_department_sales ON mv_department_sales(department_id);

-- Optional refreshes when base tables change
REFRESH MATERIALIZED VIEW mv_top_products;
REFRESH MATERIALIZED VIEW mv_department_sales;
REFRESH MATERIALIZED VIEW mv_reorder_rate;
REFRESH MATERIALIZED VIEW mv_orders_by_hour;
REFRESH MATERIALIZED VIEW mv_basket_size;

-- Validation queries
SELECT COUNT(*) AS fact_row_count FROM fact_order_products;

SELECT *
FROM mv_top_products
ORDER BY total_orders DESC
LIMIT 20;

SELECT *
FROM mv_department_sales
ORDER BY total_orders DESC;

SELECT *
FROM mv_reorder_rate
ORDER BY total_count DESC;

SELECT *
FROM mv_orders_by_hour
ORDER BY total_orders DESC;

SELECT *
FROM mv_basket_size
ORDER BY basket_size DESC
LIMIT 20;
