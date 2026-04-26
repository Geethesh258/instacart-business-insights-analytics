# 🛒 Instacart Business Insights Analytics  
### End-to-End ETL + SQL + Power BI Data Analytics Project

![Python](https://img.shields.io/badge/Python-ETL-blue)
![SQL](https://img.shields.io/badge/SQL-Analytics-green)
![PowerBI](https://img.shields.io/badge/PowerBI-Dashboard-yellow)

---

# 🧩 Business Problem

Instacart generates massive volumes of transactional order data, but lacks clear visibility into:

- Customer purchasing behavior  
- Product-level contribution to revenue  
- Department performance and growth gaps  
- Basket size impact on sales  
- Peak ordering patterns  

Without structured analytics, it becomes difficult to answer:

- What drives higher order volume?  
- Which products and departments generate the most value?  
- How customer behavior influences revenue?  
- Where growth opportunities exist in the business?  

This limits the ability to design **data-driven strategies for revenue growth, retention, and operational efficiency**.

---

# 🎯 Solution / Analytical Approach

An **end-to-end analytics pipeline** was built using **Python, SQL, and Power BI**.

## 1️⃣ Data Engineering (ETL Pipeline)
- Data cleaning and preprocessing using Python (Pandas)  
- Handling missing and inconsistent data  
- Transforming raw data into structured format  
- Building a reusable ETL pipeline  

## 2️⃣ Data Modeling (Star Schema)
- Designed a **Star Schema** for efficient analytics  
- Fact table: Orders  
- Dimension tables: Products, Departments, Time  

👉 Benefit:
- Faster query performance  
- Scalable analytics  
- Better BI integration  

## 3️⃣ Business Analysis (SQL)
- Complex joins across multiple tables  
- Aggregations for sales and behavior insights  
- SQL optimization (query tuning)  
- Basket and customer behavior segmentation  

## 4️⃣ Visualization (Power BI)
- Built interactive dashboards to analyze:
  - Customer behavior  
  - Product performance  
  - Department contribution  
  - Order timing patterns  

---

# 📊 Dashboard Overview

### 🔹 Executive Summary
![Executive Dashboard](outputs/Images/Executive.png)

- Avg basket size ≈ 10 items  
- Medium baskets contribute ~45–50% of orders  
- Reorders ~55–60% → strong retention  

---

### 🔹 Product Performance & Loyalty Analysis
![Product Dashboard](outputs/Images/Product.png)

- Top products contribute ~30–40% of total orders  
- High reorder rate (0.75–0.85) → strong loyalty  
- Majority products fall under low loyalty segment  

---

### 🔹 Department Performance & Growth Opportunities
![Department Dashboard](outputs/Images/Department.png)

- Top 5 departments contribute ~75–80% of total orders  
- Low-performing departments show high growth potential  

---

### 🔹 Basket Behavior & Order Timing
![Basket Dashboard](outputs/Images/Basket.png)

- Peak ordering time: **10 AM – 3 PM**  
- Medium baskets dominate revenue (~50–55%)  
- Large baskets underutilized  

---

# 📈 Business Insights & Impact

### 🛍️ Customer Behavior
- Reorders contribute **~55–60% of total orders**

👉 Improving reorder rate by **+5%**  
➡️ Can increase total orders by **~3–5%**

---

### 📦 Basket Strategy
- Medium baskets = **~50–55% revenue**
- Large baskets = **~15–20% only**

👉 Converting 10–15% of medium → large baskets  
➡️ Revenue increase of **~8–12%**

---

### 🛒 Product Strategy
- Top products = **~30–40% of orders**

👉 Improving product visibility  
➡️ Revenue uplift of **~3–5%**

👉 Optimizing low-performing products  
➡️ Additional **~5–7% growth**

---

### 🏬 Department Optimization
- Top departments = **~75–80% of orders**

👉 Improving low-performing departments  
➡️ **~5–8% increase in total orders**

---

### ⏰ Time-Based Demand
- Peak hours: **10 AM – 3 PM**

👉 Promotions during peak hours  
➡️ **+5–10% orders**

👉 Off-peak optimization  
➡️ **+3–5% demand**

---

# 🚀 Action Plan for Business Growth

### 🎯 Peak Hour Optimization
- Target promotions during peak time  
➡️ **+5–10% orders**

---

### 📦 Basket Expansion
- Bundle products to increase basket size  
➡️ **+8–12% revenue**

---

### 🛒 Product Optimization
- Promote top SKUs & improve low performers  
➡️ **+3–7% growth**

---

### 🏬 Department Improvement
- Focus on high-potential, low-performing departments  
➡️ **+5–8% orders**

---

### 🔁 Retention Strategy
- Loyalty programs & reorder incentives  
➡️ **+3–6% repeat purchases**

---

# 📊 Overall Business Impact

If implemented together:

- 📈 Revenue Growth: **~15–25%**
- 📦 Order Volume Increase: **~10–20%**
- 🔁 Retention Improvement: **~5–10%**

---

# 🛠 Tools & Technologies

- **Python (Pandas)** – ETL pipeline  
- **SQL** – Analysis & optimization  
- **Power BI** – Dashboard visualization  
- **Data Modeling** – Star Schema  

---

# 🧠 Skills Demonstrated

- ETL Pipeline Development  
- Data Modeling (Star Schema)  
- SQL Optimization & Advanced Queries  
- Business Analytics  
- Data Visualization  
- Insight Generation & Storytelling  

---

# 📂 Project Structure

```text
instacart-business-insights-analytics/
│
├── data/
├── notebooks/
├── sql/
├── dashboards/
├── outputs/
│   └── Images/
│       ├── Executive.png
│       ├── Product.png
│       ├── Department.png
│       └── Basket.png
└── README.md

---

# 📊 Outcome

This project demonstrates how raw transactional data can be transformed into **actionable business insights** using:

- Data Engineering (ETL)  
- Data Modeling (Star Schema)  
- SQL Analytics  
- Dashboard Visualization  

It reflects real-world Data Analyst responsibilities, combining **technical execution with business problem-solving**.

---

# 🔗 Author

**Geethesh**  
Aspiring Data Analyst | Business Analyst  
SQL | Python | Power BI
