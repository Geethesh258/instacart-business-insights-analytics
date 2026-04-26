import argparse
import os
import re
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, inspect, text


DEFAULT_DB_NAME = os.getenv("PGDATABASE", "Instacart_Dw")
DEFAULT_DB_USER = os.getenv("PGUSER", "postgres")
DEFAULT_DB_PASSWORD = os.getenv("PGPASSWORD", "root123")
DEFAULT_DB_HOST = os.getenv("PGHOST", "localhost")
DEFAULT_DB_PORT = os.getenv("PGPORT", "5432")


def normalize_identifier(value: str, prefix: str = "col") -> str:
    """Normalize names into lowercase snake_case SQL-safe identifiers."""
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    if not cleaned:
        cleaned = prefix
    if cleaned[0].isdigit():
        cleaned = f"{prefix}_{cleaned}"
    return cleaned


def build_engine(db_name: str, db_user: str, db_password: str, db_host: str, db_port: str):
    connection_url = (
        f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    return create_engine(connection_url)


def discover_csv_files(folder: Path):
    return sorted([f for f in folder.iterdir() if f.is_file() and f.suffix.lower() == ".csv"])


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    new_columns = []
    used = set()
    for raw_col in df.columns:
        col = normalize_identifier(str(raw_col), prefix="col")
        base = col
        i = 1
        while col in used:
            i += 1
            col = f"{base}_{i}"
        used.add(col)
        new_columns.append(col)
    df.columns = new_columns
    return df


def load_csv_tables(engine, csv_folder: Path, target_schema: str, if_exists: str):
    files = discover_csv_files(csv_folder)
    if not files:
        raise FileNotFoundError(f"No CSV files found in: {csv_folder}")

    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {target_schema}"))

    loaded_tables = []
    for csv_file in files:
        table_name = normalize_identifier(csv_file.stem, prefix="tbl")
        df = pd.read_csv(csv_file)
        df = standardize_columns(df)
        df["loaded_at"] = pd.Timestamp.now("UTC")

        df.to_sql(
            name=table_name,
            con=engine,
            schema=target_schema,
            if_exists=if_exists,
            index=False,
            method="multi",
            chunksize=10000,
        )

        loaded_tables.append((table_name, len(df), list(df.columns)))
        print(f"Loaded {target_schema}.{table_name} -> {len(df)} rows")

    return loaded_tables


def create_reporting_views(engine, source_schema: str, view_schema: str, table_names):
    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {view_schema}"))
        for table in table_names:
            view_name = f"v_{table}"
            conn.execute(
                text(
                    f"CREATE OR REPLACE VIEW {view_schema}.{view_name} "
                    f"AS SELECT * FROM {source_schema}.{table}"
                )
            )
            print(f"Created view {view_schema}.{view_name}")


def create_useful_indexes(engine, schema: str, loaded_tables):
    inspector = inspect(engine)
    preferred_tokens = (
        "id",
        "date",
        "hour",
        "department",
        "product",
        "user",
        "order",
        "basket",
        "reorder",
        "rank",
        "pct",
        "percent",
    )

    with engine.begin() as conn:
        for table_name, _, _ in loaded_tables:
            columns = [c["name"] for c in inspector.get_columns(table_name, schema=schema)]
            candidates = [
                c
                for c in columns
                if c != "loaded_at" and any(token in c for token in preferred_tokens)
            ][:4]

            for col in candidates:
                idx_name = normalize_identifier(f"idx_{table_name}_{col}", prefix="idx")
                conn.execute(
                    text(
                        f"CREATE INDEX IF NOT EXISTS {idx_name} "
                        f"ON {schema}.{table_name} ({col})"
                    )
                )
                print(f"Created index {idx_name} on {schema}.{table_name}({col})")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Load final analysis CSV tables into PostgreSQL for Power BI consumption."
    )
    parser.add_argument(
        "--csv-folder",
        default="outputs/tables",
        help="Folder containing final analysis CSV files.",
    )
    parser.add_argument("--db-name", default=DEFAULT_DB_NAME)
    parser.add_argument("--db-user", default=DEFAULT_DB_USER)
    parser.add_argument("--db-password", default=DEFAULT_DB_PASSWORD)
    parser.add_argument("--db-host", default=DEFAULT_DB_HOST)
    parser.add_argument("--db-port", default=DEFAULT_DB_PORT)
    parser.add_argument(
        "--target-schema",
        default="bi",
        help="Schema where final tables are loaded.",
    )
    parser.add_argument(
        "--if-exists",
        choices=["replace", "append"],
        default="replace",
        help="replace: recreate table each run, append: add rows to existing table.",
    )
    parser.add_argument(
        "--create-views",
        action="store_true",
        help="Create BI reporting views (v_<table_name>) in reporting schema.",
    )
    parser.add_argument(
        "--view-schema",
        default="bi_reporting",
        help="Schema where BI views are created.",
    )
    parser.add_argument(
        "--create-indexes",
        action="store_true",
        help="Create helpful indexes for common Power BI filters.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    csv_folder = Path(args.csv_folder)
    if not csv_folder.exists():
        raise FileNotFoundError(f"CSV folder not found: {csv_folder}")

    engine = build_engine(
        db_name=args.db_name,
        db_user=args.db_user,
        db_password=args.db_password,
        db_host=args.db_host,
        db_port=args.db_port,
    )

    loaded_tables = load_csv_tables(
        engine=engine,
        csv_folder=csv_folder,
        target_schema=args.target_schema,
        if_exists=args.if_exists,
    )

    table_names = [t[0] for t in loaded_tables]

    if args.create_views:
        create_reporting_views(
            engine=engine,
            source_schema=args.target_schema,
            view_schema=args.view_schema,
            table_names=table_names,
        )

    if args.create_indexes:
        create_useful_indexes(
            engine=engine,
            schema=args.target_schema,
            loaded_tables=loaded_tables,
        )

    print("Done. Final analysis tables are ready in PostgreSQL.")


if __name__ == "__main__":
    main()
