import os

import pandas as pd
import psycopg2


DEFAULT_DB_NAME = os.getenv("PGDATABASE", "Instacart_Dw")
DEFAULT_DB_USER = os.getenv("PGUSER", "postgres")
DEFAULT_DB_PASSWORD = os.getenv("PGPASSWORD", "root123")
DEFAULT_DB_HOST = os.getenv("PGHOST", "localhost")
DEFAULT_DB_PORT = os.getenv("PGPORT", "5432")


def get_connection():
    return psycopg2.connect(
        dbname=DEFAULT_DB_NAME,
        user=DEFAULT_DB_USER,
        password=DEFAULT_DB_PASSWORD,
        host=DEFAULT_DB_HOST,
        port=DEFAULT_DB_PORT,
    )

def load_data(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df