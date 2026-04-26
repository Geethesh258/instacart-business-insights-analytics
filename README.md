# Instacart Analytics (Executable Project)

This project generates analysis tables/charts from PostgreSQL materialized views and can also load final CSV outputs back into PostgreSQL for Power BI.

## 1) Prerequisites

- Python 3.10+
- PostgreSQL running with the Instacart warehouse database
- Accessible views used by this project (for example: `mv_reorder_rate`, `mv_reorder_product_v2`, `mv_reorder_department_v2`, `mv_reorder_time_v2`, `mv_orders_time_v2`, `mv_product_performance_v2`, `mv_department_performance_v2`, `mv_basket_analysis_v2`)

## 2) Setup

From project root:

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

## 3) Database Configuration

Set environment variables (PowerShell example):

```powershell
$env:PGDATABASE = "Instacart_Dw"
$env:PGUSER = "postgres"
$env:PGPASSWORD = "root123"
$env:PGHOST = "localhost"
$env:PGPORT = "5432"
```

If these are not set, defaults above are used.

## 4) Run the Project (One Command)

Generate all analysis outputs:

```bash
python run_project.py
```

Windows shortcut:

```powershell
run_project.bat
```

This creates/updates:
- `outputs/charts/*.png`
- `outputs/tables/*.csv`

## 5) Optional: Load CSV Outputs to PostgreSQL

Run analysis and then load tables to PostgreSQL schema `bi`:

```bash
python run_project.py --load-to-postgres --create-views --create-indexes
```

If CSV outputs already exist and you only want to load:

```bash
python run_project.py --skip-analysis --load-to-postgres
```

## 6) Legacy Commands (Still Supported)

Run analysis only:

```bash
python -m src.analysis
```

Run loader only:

```bash
python -m src.load_analysis_tables_to_postgres --create-views --create-indexes
```

## 7) Submission Tip

For your college demo, run this in front of your teacher:

```bash
python run_project.py --load-to-postgres --create-views --create-indexes
```

That proves the project is executable end-to-end.
