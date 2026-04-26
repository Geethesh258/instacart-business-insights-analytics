# Instacart SQL Analytics

## What This SQL Solves
This SQL layer turns raw order-level Instacart data into business decisions for growth, retention, and category performance.

Core business problems solved:
1. Which products and departments drive the highest order volume and repeat behavior?
2. When do customers place orders, and when is reorder propensity highest?
3. How large are baskets, and where can cross-sell opportunities increase basket value?
4. Which customer and product patterns indicate retention strength or risk?

Measured business impact this model is designed to enable (through downstream actions):
1. Revenue growth potential: 3% to 8% via product mix optimization and basket expansion.
2. Order lift potential: 2% to 6% via hour-level campaign timing and category targeting.
3. Retention improvement potential: 2 to 5 percentage points via reorder-focused CRM strategies.

Note: these percentages are execution targets enabled by analytics outputs and should be validated through experiments or historical A/B comparisons.

## Analytics Engineering Approach
The project follows a practical ELT pattern in PostgreSQL:

1. Stage raw datasets into clean staging tables.
2. Profile data quality with row counts, null checks, duplicate checks, and key sanity checks.
3. Transform staging data into a star schema:
   - Fact table: order-product transaction events.
   - Dimension tables: orders, products, aisles, departments.
4. Build materialized views for BI and recurring dashboard use.
5. Add constraints and indexes for data integrity and query performance.

Why star schema was used:
1. Faster analytical querying for dashboards and stakeholder exploration.
2. Cleaner separation of transaction events versus descriptive attributes.
3. Easier extensibility for new KPIs without redesigning the whole model.

## SQL Techniques Used
1. Joins: inner and full outer joins to combine behavioral, product, and hierarchy data.
2. Aggregations: COUNT, SUM, grouped KPI rollups for product, department, hour, and basket analytics.
3. CTEs: structured intermediate logic for readability and reusable metric calculations.
4. Window functions: ranking and distribution logic for duplicate checks and rate calculations.
5. Indexing: targeted indexes on high-filter columns to improve dashboard responsiveness.
6. Materialized views: precomputed KPI layers for faster reporting.
7. Query optimization: idempotent DDL, explicit dependency order, and defensive calculations using NULLIF.

## Query to Business Insight Mapping

| Query Type | Business Question | Insight |
|---|---|---|
| Reorder rate by product | Which products create habitual buying behavior? | High reorder products identify strong retention anchors and recurring demand drivers. |
| Reorder rate by department | Which categories build long-term loyalty? | Departments with stronger reorder rates are priority candidates for retention campaigns and bundle offers. |
| Orders by hour | When should promotions and notifications run? | Hourly order concentration reveals optimal campaign windows to improve conversion. |
| Basket size distribution | How can average order value be increased? | Basket bands show where cross-sell and upsell interventions can move small baskets upward. |
| Top products by volume | Which SKUs contribute most to order throughput? | High-frequency SKUs should be protected in inventory and highlighted in merchandising. |
| Data quality and duplicate checks | Can stakeholders trust KPI outputs? | Early anomaly detection reduces reporting risk and improves confidence in decision-making. |

## File-by-File Explanation
1. instacart.sql
   - Builds staging tables and runs foundational data profiling and quality checks.

2. instacart_facttable.sql
   - Creates star schema tables, applies primary and foreign keys, and adds performance indexes.

3. instacart_matview_aggr.sql
   - Produces advanced materialized views for executive KPIs, reorder intelligence, department trends, and time analysis.

4. instacart_view_and_aggregation.sql
   - Adds business-friendly summary views for quick consumption in BI tools and stakeholder reporting.

## Execution Flow
Run scripts in this order:

1. instacart.sql
2. instacart_facttable.sql
3. instacart_matview_aggr.sql
4. instacart_view_and_aggregation.sql

Execution guidance:
1. Ensure raw data is loaded before running transformations.
2. Run in PostgreSQL via psql, pgAdmin, or DBeaver.
3. Re-run safely using idempotent drop/create patterns.

## Business Impact Enabled
With this SQL layer in place, analytics teams can operationalize:

1. Revenue acceleration:
   - Product and category optimization workflows that can support 3% to 8% revenue growth.

2. Order frequency growth:
   - Time-slot and reorder-triggered actions that can support 2% to 6% order uplift.

3. Retention gains:
   - Reorder and loyalty segmentation that can support 2 to 5 percentage-point retention improvement.

4. Decision speed:
   - Materialized-view-based reporting that reduces repeated heavy query execution and improves dashboard responsiveness.
