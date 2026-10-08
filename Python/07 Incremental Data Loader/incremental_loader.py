"""
Incremental Data Loader (project 07)
====================================

What this file does
-------------------
Load ONLY new and updated records into a SQL table. Unchanged rows and
stale rows (older than what is already stored) are skipped.

Project 01 emptied the table and reloaded everything. That is fine for
a small CSV. It is a bad habit on a large warehouse table: you rewrite
rows that did not change, and you can briefly look empty mid-job.

Two incremental ideas (this script shows both)
----------------------------------------------
1. Business-key compare
   Incoming order_id vs the table. New ids insert. Existing ids with a
   newer updated_at update. Older updated_at is stale and ignored.

2. Watermark
   Remember the latest updated_at you successfully applied. The next
   extract can ask the source "give me rows after this timestamp."
   APIs and SQL sources can filter that way. A full CSV dump still
   needs the row compare in (1).

Decisions baked into this version
---------------------------------
* Same orders schema as project 01, but this folder is self-contained.
  It seeds SQLite from warehouse_orders.csv (stand-in for "already
  loaded") then applies incoming_orders.csv (stand-in for "today's
  extract"). Point db_path at project 01's orders.db if you want them
  chained.

* Classify in Pandas, then UPSERT in SQL
  The printed NEW / UPDATED / STALE / UNCHANGED counts are the point
  of the lesson. The INSERT ... ON CONFLICT statement is how SQLite
  applies the keepers. SQL Server uses MERGE; Postgres uses the same
  ON CONFLICT shape.

* updated_at is the "is this newer?" field
  A status change with the same timestamp would look unchanged. In a
  real system the source should bump updated_at on every edit. If it
  does not, people hash the whole row instead.

Planted rows in incoming_orders.csv
-----------------------------------
  1001  older updated_at than warehouse     -> STALE (skip)
  1002  pending -> shipped, later timestamp -> UPDATED
  1004  identical to warehouse              -> UNCHANGED (skip)
  1006  new order_id                        -> NEW
  1007  new order_id                        -> NEW

How to run
----------
    python incremental_loader.py

Needs: pandas, sqlalchemy
"""

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text


SCRIPT_DIR = Path(__file__).resolve().parent
WAREHOUSE_CSV = SCRIPT_DIR / "warehouse_orders.csv"
INCOMING_CSV = SCRIPT_DIR / "incoming_orders.csv"
DB_PATH = SCRIPT_DIR / "orders.db"
ENGINE_URL = f"sqlite:///{DB_PATH.as_posix()}"
WATERMARK_NAME = "orders_incremental"

COLUMNS = [
    "order_id",
    "customer_id",
    "order_date",
    "product",
    "quantity",
    "unit_price",
    "status",
    "updated_at",
]

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

CREATE_WATERMARK_SQL = """
CREATE TABLE IF NOT EXISTS etl_watermark (
    pipeline_name   TEXT NOT NULL PRIMARY KEY,
    last_updated_at TEXT NOT NULL
)
"""

UPSERT_SQL = """
INSERT INTO orders (
    order_id, customer_id, order_date, product,
    quantity, unit_price, status, updated_at
) VALUES (
    :order_id, :customer_id, :order_date, :product,
    :quantity, :unit_price, :status, :updated_at
)
ON CONFLICT(order_id) DO UPDATE SET
    customer_id = excluded.customer_id,
    order_date  = excluded.order_date,
    product     = excluded.product,
    quantity    = excluded.quantity,
    unit_price  = excluded.unit_price,
    status      = excluded.status,
    updated_at  = excluded.updated_at
WHERE excluded.updated_at > orders.updated_at
"""


def read_orders_csv(path):
    df = pd.read_csv(path)
    missing = [col for col in COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"{path.name} missing columns: {', '.join(missing)}")
    df = df[COLUMNS].copy()
    df["order_id"] = df["order_id"].astype(int)
    return df


def seed_warehouse(engine, warehouse_df):
    """Pretend project 01 already ran: table holds yesterday's load."""
    with engine.begin() as conn:
        conn.execute(text(CREATE_ORDERS_SQL))
        conn.execute(text(CREATE_WATERMARK_SQL))
        conn.execute(text("DELETE FROM orders"))
        warehouse_df.to_sql("orders", conn, if_exists="append", index=False)
    print(f"Seeded warehouse with {len(warehouse_df)} row(s) from {WAREHOUSE_CSV.name}")


def load_destination(engine):
    with engine.connect() as conn:
        return pd.read_sql(text("SELECT * FROM orders"), conn)


def classify(incoming, destination):
    """Compare incoming rows to what is already in SQL.

    Returns a dict of DataFrames, one per bucket, so the report can
    show *why* each order_id was kept or skipped.
    """
    dest = destination.set_index("order_id")
    buckets = {name: [] for name in ("new", "updated", "unchanged", "stale")}

    for _, row in incoming.iterrows():
        order_id = int(row["order_id"])
        if order_id not in dest.index:
            buckets["new"].append(row)
            continue

        incoming_ts = str(row["updated_at"])
        dest_ts = str(dest.loc[order_id, "updated_at"])
        if incoming_ts > dest_ts:
            buckets["updated"].append(row)
        elif incoming_ts < dest_ts:
            buckets["stale"].append(row)
        else:
            buckets["unchanged"].append(row)

    return {name: pd.DataFrame(rows, columns=COLUMNS) for name, rows in buckets.items()}


def print_report(buckets):
    print("\nIncremental classification")
    print("--------------------------")
    for name in ("new", "updated", "unchanged", "stale"):
        df = buckets[name]
        ids = ", ".join(df["order_id"].astype(str)) if not df.empty else "(none)"
        print(f"  {name:10} {len(df)}  order_id {ids}")

    if not buckets["updated"].empty:
        print("\nUpdated rows (incoming status vs what changed):")
        print(buckets["updated"][["order_id", "status", "updated_at"]].to_string(index=False))


def upsert_rows(engine, df):
    if df.empty:
        return 0
    records = df.to_dict(orient="records")
    with engine.begin() as conn:
        conn.execute(text(UPSERT_SQL), records)
    return len(records)


def write_watermark(engine, timestamp):
    sql = text("""
        INSERT INTO etl_watermark (pipeline_name, last_updated_at)
        VALUES (:name, :ts)
        ON CONFLICT(pipeline_name) DO UPDATE SET last_updated_at = excluded.last_updated_at
    """)
    with engine.begin() as conn:
        conn.execute(sql, {"name": WATERMARK_NAME, "ts": timestamp})
    print(f"\nWatermark '{WATERMARK_NAME}' set to {timestamp}")


def preview_table(engine):
    with engine.connect() as conn:
        orders = pd.read_sql(
            text("SELECT order_id, product, status, updated_at FROM orders ORDER BY order_id"),
            conn,
        )
        mark = conn.execute(
            text("SELECT last_updated_at FROM etl_watermark WHERE pipeline_name = :n"),
            {"n": WATERMARK_NAME},
        ).scalar()
    print("\norders after incremental load:")
    print(orders.to_string(index=False))
    print(f"\nStored watermark: {mark}")


def main():
    warehouse = read_orders_csv(WAREHOUSE_CSV)
    incoming = read_orders_csv(INCOMING_CSV)

    engine = create_engine(ENGINE_URL)
    seed_warehouse(engine, warehouse)
    destination = load_destination(engine)

    buckets = classify(incoming, destination)
    print_report(buckets)

    applied = pd.concat([buckets["new"], buckets["updated"]], ignore_index=True)
    written = upsert_rows(engine, applied)
    print(f"\nUpserted {written} row(s) (new + updated).")

    if not applied.empty:
        write_watermark(engine, applied["updated_at"].max())

    preview_table(engine)
    print("\nSkipped stale/unchanged rows on purpose. Re-run the script; the seed resets, so the report stays the same.")


if __name__ == "__main__":
    main()
