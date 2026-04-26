from .db import load_data

# Overview KPIs
overview = load_data("SELECT * FROM mv_overview_kpis_v2")

# Product Performance
top_products = load_data("SELECT * FROM mv_product_performance_v2")

# Department Performance
category = load_data("SELECT * FROM mv_department_performance_v2")

# Reorder Analysis
reorder_product = load_data("SELECT * FROM mv_reorder_product_v2")
reorder_department = load_data("SELECT * FROM mv_reorder_department_v2")

# Time Analysis
time_data = load_data("SELECT * FROM mv_orders_time_v2")
reorder_time = load_data("SELECT * FROM mv_reorder_time_v2")

# Basket Analysis
basket = load_data("SELECT * FROM mv_basket_analysis_v2")