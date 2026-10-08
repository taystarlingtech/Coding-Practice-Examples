"""
Runnable Reporting Workshop (SQL folder)
========================================

Why this exists
---------------
The other files in this SQL folder are production-style Infinium / SSMS
queries. They are strong evidence of real work, but a reviewer cannot
run them (no access to psa.dbo, no PRPMS table).

This workshop is the version you CAN run and the version you can study
before an interview: readable names, CTEs, window functions, CASE, and
the same self-join org-chart idea as Ops Org Chart Query.sql.

SQLite vs SQL Server
--------------------
Python's sqlite3 module is in the standard library - no extra install.
SQL Server dialect differences you already know (NOLOCK, RIGHT(),
CONVERT) are called out in the .sql comments. The join logic transfers.

How to run
----------
    python reporting_workshop.py

Creates hr.db next to this script, runs each query in sql/, prints
the result tables. Re-running rebuilds the database from scratch.
"""

import sqlite3
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SQL_DIR = SCRIPT_DIR / "sql"
DB_PATH = SCRIPT_DIR / "hr.db"

# Order matters: schema and seed first, then the study queries.
QUERY_FILES = [
    "00_schema.sql",
    "01_seed.sql",
    "02_org_chart.sql",
    "03_headcount_cte.sql",
    "04_window_functions.sql",
    "05_case_mapping.sql",
    "06_exception_report.sql",
]


def run_script(conn, path):
    """Execute a whole .sql file (schema/seed may contain multiple statements)."""
    sql = path.read_text(encoding="utf-8")
    conn.executescript(sql)


def run_query(conn, path):
    """Run a SELECT file and return (column_names, rows)."""
    sql = path.read_text(encoding="utf-8")
    cursor = conn.execute(sql)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    return columns, rows


def print_table(title, columns, rows):
    print()
    print("=" * 64)
    print(title)
    print("=" * 64)
    if not rows:
        print("(no rows)")
        return

    widths = [len(col) for col in columns]
    for row in rows:
        for i, value in enumerate(row):
            widths[i] = max(widths[i], len(str(value)))

    header = "  ".join(col.ljust(widths[i]) for i, col in enumerate(columns))
    print(header)
    print("  ".join("-" * w for w in widths))
    for row in rows:
        print("  ".join(str(value).ljust(widths[i]) for i, value in enumerate(row)))
    print(f"({len(rows)} row(s))")


def main():
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    try:
        print(f"Building {DB_PATH.name} from sql/00_schema.sql + sql/01_seed.sql")
        run_script(conn, SQL_DIR / "00_schema.sql")
        run_script(conn, SQL_DIR / "01_seed.sql")
        conn.commit()

        count = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
        print(f"Seeded {count} employee row(s).")

        for name in QUERY_FILES:
            if name.startswith("00_") or name.startswith("01_"):
                continue
            columns, rows = run_query(conn, SQL_DIR / name)
            print_table(name, columns, rows)
    finally:
        conn.close()

    print()
    print("Done. Open the .sql files and compare 02_org_chart.sql with Ops Org Chart Query.sql.")


if __name__ == "__main__":
    main()
