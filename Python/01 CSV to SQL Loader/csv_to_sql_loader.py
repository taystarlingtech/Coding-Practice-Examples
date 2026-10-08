"""
CSV to SQL Loader (project 01)
==============================

What this file does
-------------------
Take a raw CSV and load it into a SQL table. That is the "first load"
pattern: the table should match the file after the script runs.

It does NOT check data quality (project 04) and it does NOT skip rows
that were already loaded (project 07). Those come later in a pipeline.

Decisions baked into this version
---------------------------------
* SQLite instead of SQL Server / Postgres
  No server to install. The database is a file next to this script.
  The SQLAlchemy URL is the only line you would change for Postgres:
      sqlite:///orders.db
      postgresql+psycopg2://user:pass@localhost/warehouse

* CREATE TABLE yourself, then insert
  Pandas df.to_sql() can guess column types. Guessing turns order_id
  into REAL, dates into TEXT of mixed formats, and you lose a primary
  key. Explicit DDL is the same habit as creating a table in SSMS.

* Full refresh (DELETE then INSERT), not an upsert
  Project 01 is "make the table look like this file." Project 07 is
  "only apply new and changed rows." Mixing those here hides the
  difference.

How to run
----------
    python csv_to_sql_loader.py

Needs: pandas, sqlalchemy
Writes orders.db next to this script.
"""

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text


SCRIPT_DIR = Path(__file__).resolve().parent
CSV_PATH = SCRIPT_DIR / "sample_orders.csv"
DB_PATH = SCRIPT_DIR / "orders.db"

# sqlite:/// needs a forward-slash URL even on Windows.
ENGINE_URL = f"sqlite:///{DB_PATH.as_posix()}"

# SQLite stores dates as TEXT. Using ISO-8601 strings (YYYY-MM-DD and
# YYYY-MM-DDTHH:MM:SS) means they still sort correctly as text.
CREATE_ORDERS_SQL = """
CREATE TABLE IF NOT EXISTS orders (
    order_id    INTEGER NOT NULL PRIMARY KEY,
    customer_id TEXT    NOT NULL,
    order_date  TEXT    NOT NULL,
    product     TEXT    NOT NULL,
    quantity    INTEGER NOT NULL,
    unit_price  REAL    NOT NULL,
    status      TEXT    NOT NULL,
    updated_at  TEXT    NOT NULL
)
"""

EXPECTED_COLUMNS = [
    "order_id",
    "customer_id",
    "order_date",
    "product",
    "quantity",
    "unit_price",
    "status",
    "updated_at",
]


def read_csv(path):
    """Load the CSV and fail early if the headers do not match the table."""
    if not path.exists():
        raise FileNotFoundError(f"Could not find {path.name}. Keep it next to this script.")

    df = pd.read_csv(path)
    missing = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    extra = [col for col in df.columns if col not in EXPECTED_COLUMNS]
    if missing:
        raise ValueError(f"CSV is missing columns: {', '.join(missing)}")
    if extra:
        # Extra columns are dropped, not loaded. Better to notice than to
        # silently invent table columns from a messy export.
        print(f"Ignoring extra CSV column(s): {', '.join(extra)}")

    df = df[EXPECTED_COLUMNS].copy()
    df["order_id"] = df["order_id"].astype(int)
    df["quantity"] = df["quantity"].astype(int)
    df["unit_price"] = df["unit_price"].astype(float)
    return df


def load_full_refresh(df, engine):
    """Create the table if needed, empty it, then insert every CSV row.

    engine.begin() starts a transaction. If the insert fails, the DELETE
    rolls back and you do not get a half-empty table.
    """
    with engine.begin() as conn:
        conn.execute(text(CREATE_ORDERS_SQL))
        deleted = conn.execute(text("DELETE FROM orders")).rowcount
        print(f"Cleared {deleted} existing row(s).")
        # if_exists="append" keeps our CREATE TABLE (and the primary key).
        # "replace" would drop the table and let Pandas rebuild it without a PK.
        df.to_sql("orders", conn, if_exists="append", index=False)


def preview_table(engine):
    """Read back from SQL so you can see the round-trip, not just the CSV."""
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM orders")).scalar_one()
        print(f"orders table now has {count} row(s).")
        sample = pd.read_sql(
            text("SELECT order_id, customer_id, product, status, updated_at FROM orders ORDER BY order_id"),
            conn,
        )
    print("\nLoaded rows:")
    print(sample.to_string(index=False))


def main():
    print(f"Reading {CSV_PATH.name}")
    orders = read_csv(CSV_PATH)
    print(f"CSV rows: {len(orders)}")

    engine = create_engine(ENGINE_URL)
    print(f"Loading into {DB_PATH.name}")
    load_full_refresh(orders, engine)
    preview_table(engine)
    print("\nFull refresh complete. For later loads of only new/changed rows, see project 07.")


if __name__ == "__main__":
    main()
