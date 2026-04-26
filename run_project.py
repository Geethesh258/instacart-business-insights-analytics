import argparse
from pathlib import Path

from src.analysis import main as run_analysis
from src.load_analysis_tables_to_postgres import (
    DEFAULT_DB_HOST,
    DEFAULT_DB_NAME,
    DEFAULT_DB_PASSWORD,
    DEFAULT_DB_PORT,
    DEFAULT_DB_USER,
    build_engine,
    create_reporting_views,
    create_useful_indexes,
    load_csv_tables,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Instacart analytics pipeline and optionally load outputs to PostgreSQL."
    )
    parser.add_argument(
        "--skip-analysis",
        action="store_true",
        help="Skip analysis generation and only run the PostgreSQL load stage.",
    )
    parser.add_argument(
        "--load-to-postgres",
        action="store_true",
        help="Load generated CSV outputs in outputs/tables into PostgreSQL.",
    )
    parser.add_argument(
        "--csv-folder",
        default="outputs/tables",
        help="Folder containing CSV tables to load into PostgreSQL.",
    )
    parser.add_argument("--db-name", default=DEFAULT_DB_NAME)
    parser.add_argument("--db-user", default=DEFAULT_DB_USER)
    parser.add_argument("--db-password", default=DEFAULT_DB_PASSWORD)
    parser.add_argument("--db-host", default=DEFAULT_DB_HOST)
    parser.add_argument("--db-port", default=DEFAULT_DB_PORT)
    parser.add_argument("--target-schema", default="bi")
    parser.add_argument("--if-exists", choices=["replace", "append"], default="replace")
    parser.add_argument("--create-views", action="store_true")
    parser.add_argument("--view-schema", default="bi_reporting")
    parser.add_argument("--create-indexes", action="store_true")
    return parser.parse_args()


def run_loader(args: argparse.Namespace) -> None:
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

    table_names = [table_name for table_name, _, _ in loaded_tables]

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

    print("Done. Final analysis tables are loaded to PostgreSQL.")


def main() -> None:
    args = parse_args()

    if not args.skip_analysis:
        print("Step 1/2: Running analytics pipeline...")
        run_analysis()

    if args.load_to_postgres:
        print("Step 2/2: Loading CSV outputs to PostgreSQL...")
        run_loader(args)

    if args.skip_analysis and not args.load_to_postgres:
        print("Nothing to do. Use --load-to-postgres or remove --skip-analysis.")


if __name__ == "__main__":
    main()
