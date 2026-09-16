"""
Data Quality Checker (project 04)
=================================

What this file does
-------------------
A data quality checker is a script that looks at a table and asks:
"Is this data safe to load / report on?"

It does NOT analyze sales trends. It does NOT make a dashboard.
It only validates the file against rules we decide ahead of time.

The infographic listed three core checks:
  1. Schema  - are the expected columns present, with the right kinds of values?
  2. Nulls   - are required fields actually filled in?
  3. Duplicates - did the same row (or same order id) show up more than once?

This script also adds a few extra rules that show up in real reporting work:
  - quantity must be greater than 0
  - status must be one of a known list (pending / shipped / cancelled)
  - product must be one of a known list
  - dates and numbers must actually convert (no "abc" in a price column)

How to run
----------
    python data_quality_checker.py

Put this file and sample_orders.csv in the same folder. The script looks
next to itself for the CSV, so it does not matter what folder you are in
when you run it.

Pandas vs Great Expectations
----------------------------
The infographic mentioned Pandas and Great Expectations. This version uses
Pandas only so every check is visible in one file. Great Expectations is a
library that does the same idea with YAML configs and HTML reports - useful
later, but it hides the logic while you are learning.
"""

from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# 1. The "contract" - what good data is supposed to look like
# ---------------------------------------------------------------------------
# In reporting jobs this often lives in a spec, a SQL table definition, or a
# dbt schema.yml file. Putting it in one dictionary means the rules are not
# scattered through if-statements.
#
# kind tells the checker how to try converting the column:
#   int      -> whole numbers (order_id, quantity)
#   float    -> decimals (unit_price)
#   datetime -> calendar dates (order_date)
#   string   -> text (customer_id, product, status)

EXPECTED_COLUMNS = {
    "order_id": "int",
    "customer_id": "string",
    "order_date": "datetime",
    "product": "string",
    "quantity": "int",
    "unit_price": "float",
    "status": "string",
}

# Columns that must never be empty. customer_id is required here because an
# order with no customer cannot be joined to an employee / customer table -
# the same problem your Excel join script would hit with a blank User ID.
REQUIRED_NOT_NULL = ["order_id", "customer_id", "order_date", "product", "quantity"]

# order_id is the "business key": one order should appear once.
# Full-row duplicates (every column the same) are a separate, simpler check.
BUSINESS_KEY = "order_id"

ALLOWED_STATUSES = {"pending", "shipped", "cancelled"}
ALLOWED_PRODUCTS = {"Keyboard", "Mouse", "Monitor", "Headset", "Cable"}

# sample_orders.csv sits in this same folder.
CSV_PATH = Path(__file__).resolve().parent / "sample_orders.csv"


# ---------------------------------------------------------------------------
# 2. Load the file
# ---------------------------------------------------------------------------
def load_orders(csv_path):
    """Read the CSV into a DataFrame.

    dtype=str keeps every column as text at first. That sounds backwards,
    but it is useful for quality checks: if Pandas eagerly converts a column
    to numbers, the original bad value ("abc") is already gone (turned into
    NaN) and we cannot show the reviewer what was in the file.

    We convert column-by-column later, on purpose, and report the failures.
    """
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Could not find {csv_path.name}. Keep it next to this script."
        )

    # keep_default_na=True (the default) turns empty cells into NaN.
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=True)
    # Strip accidental spaces around headers (" order_id " vs "order_id").
    df.columns = df.columns.str.strip()
    return df


# ---------------------------------------------------------------------------
# 3. Small helpers used by several checks
# ---------------------------------------------------------------------------
def coerce_column(series, kind):
    """Try to convert a text column into the expected type.

    values that cannot convert become NaN. We compare those NaNs against
    the original series to find "this cell had text, but it was not valid."
    Empty cells were already NaN, so they are NOT counted as type failures -
    they are counted as nulls instead.
    """
    if kind == "int":
        # downcast="integer" is not used here because mixed garbage like
        # "abc" should become NaN, not raise.
        return pd.to_numeric(series, errors="coerce")
    if kind == "float":
        return pd.to_numeric(series, errors="coerce")
    if kind == "datetime":
        # format="ISO8601" would be stricter; mixed formats are common in
        # exports, so we let Pandas infer and flag anything it cannot parse.
        return pd.to_datetime(series, errors="coerce")
    # "string" - nothing to convert; empty strings still count as null later.
    return series


def is_blank(series):
    """True for NaN and for cells that are only whitespace.

    CSV exports sometimes write a space instead of leaving the cell empty.
    Both should fail a "required field" check.
    """
    as_text = series.fillna("").astype(str).str.strip()
    return as_text.eq("") | series.isna()


# ---------------------------------------------------------------------------
# 4. The checks
# Each function returns a dict:
#   name     - printed in the report
#   passed   - True / False
#   message  - one-line summary
#   bad_rows - DataFrame of problem rows (may be empty)
# ---------------------------------------------------------------------------
def check_schema_columns(df):
    """Are the expected column names present? Any surprise extra columns?

    Missing columns are a hard fail: later checks cannot even run on them.
    Extra columns are also flagged. They are not always wrong (a source
    system might add a field), but they are worth noticing so you do not
    silently drop them.
    """
    expected = set(EXPECTED_COLUMNS)
    actual = set(df.columns)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)

    passed = len(missing) == 0
    parts = []
    if missing:
        parts.append("missing columns: " + ", ".join(missing))
    if extra:
        parts.append("unexpected columns: " + ", ".join(extra))
    if not parts:
        parts.append("all expected columns are present")

    # bad_rows is empty here because this check is about headers, not cells.
    return {
        "name": "Schema - column names",
        "passed": passed,
        "message": "; ".join(parts),
        "bad_rows": pd.DataFrame(),
    }


def check_schema_types(df):
    """Can each column's values convert to the type in EXPECTED_COLUMNS?

    Example: unit_price is supposed to be a float. The cell "abc" cannot
    become a number, so that row fails. A blank price is a null, not a
    type error - nulls are handled in check_nulls().
    """
    problem_frames = []

    for column, kind in EXPECTED_COLUMNS.items():
        if column not in df.columns:
            continue  # schema-name check already reported this

        original = df[column]
        converted = coerce_column(original, kind)

        # Failed conversion: original had something in it, converted is NaN.
        failed = converted.isna() & ~is_blank(original)
        if failed.any():
            snippet = df.loc[failed, [column]].copy()
            snippet.insert(0, "row_number", snippet.index + 2)  # +2 = header + 1-based
            snippet.insert(1, "expected_type", kind)
            snippet = snippet.rename(columns={column: "bad_value"})
            problem_frames.append(snippet)

    if problem_frames:
        bad_rows = pd.concat(problem_frames, ignore_index=True)
        return {
            "name": "Schema - value types",
            "passed": False,
            "message": f"{len(bad_rows)} value(s) could not convert to the expected type",
            "bad_rows": bad_rows,
        }

    return {
        "name": "Schema - value types",
        "passed": True,
        "message": "all non-empty values match the expected types",
        "bad_rows": pd.DataFrame(),
    }


def check_nulls(df):
    """Are required columns filled in?

    Optional columns (unit_price, status here) may be empty without failing
    this check. Tighten REQUIRED_NOT_NULL if those should also be required.
    """
    present = [col for col in REQUIRED_NOT_NULL if col in df.columns]
    if not present:
        return {
            "name": "Nulls - required fields",
            "passed": False,
            "message": "none of the required columns exist in the file",
            "bad_rows": pd.DataFrame(),
        }

    # A row fails if ANY required column is blank.
    blank_map = pd.DataFrame({col: is_blank(df[col]) for col in present})
    row_is_bad = blank_map.any(axis=1)

    if row_is_bad.any():
        bad_rows = df.loc[row_is_bad, present].copy()
        bad_rows.insert(0, "row_number", bad_rows.index + 2)
        return {
            "name": "Nulls - required fields",
            "passed": False,
            "message": f"{int(row_is_bad.sum())} row(s) have a blank required field",
            "bad_rows": bad_rows,
        }

    return {
        "name": "Nulls - required fields",
        "passed": True,
        "message": "every required field is filled in",
        "bad_rows": pd.DataFrame(),
    }


def check_duplicate_rows(df):
    """Exact copies of an entire row.

    keep=False marks EVERY copy as a duplicate, including the first one,
    so the report shows the full set instead of hiding the original.
    """
    duplicated = df.duplicated(keep=False)
    if duplicated.any():
        bad_rows = df.loc[duplicated].copy()
        bad_rows.insert(0, "row_number", bad_rows.index + 2)
        pair_count = int(duplicated.sum() // 2)  # two matching rows = one pair
        return {
            "name": "Duplicates - full rows",
            "passed": False,
            "message": f"{int(duplicated.sum())} row(s) are exact copies ({pair_count} pair(s))",
            "bad_rows": bad_rows,
        }

    return {
        "name": "Duplicates - full rows",
        "passed": True,
        "message": "no exact duplicate rows",
        "bad_rows": pd.DataFrame(),
    }


def check_duplicate_keys(df):
    """Same business key (order_id) appearing more than once.

    This can catch duplicates even when other columns differ - for example
    the same order_id with two different statuses. Full-row duplicate check
    would miss that.
    """
    if BUSINESS_KEY not in df.columns:
        return {
            "name": "Duplicates - business key",
            "passed": False,
            "message": f"business key column '{BUSINESS_KEY}' is missing",
            "bad_rows": pd.DataFrame(),
        }

    # Blank keys are a null problem, not a duplicate problem.
    filled = ~is_blank(df[BUSINESS_KEY])
    duplicated = df.duplicated(subset=[BUSINESS_KEY], keep=False) & filled

    if duplicated.any():
        bad_rows = df.loc[duplicated].copy()
        bad_rows.insert(0, "row_number", bad_rows.index + 2)
        unique_keys = bad_rows[BUSINESS_KEY].nunique()
        return {
            "name": "Duplicates - business key",
            "passed": False,
            "message": (
                f"{int(duplicated.sum())} row(s) share a repeated {BUSINESS_KEY} "
                f"({unique_keys} duplicated key(s))"
            ),
            "bad_rows": bad_rows,
        }

    return {
        "name": "Duplicates - business key",
        "passed": True,
        "message": f"every filled {BUSINESS_KEY} is unique",
        "bad_rows": pd.DataFrame(),
    }


def check_quantity_positive(df):
    """Quantity must be a number greater than 0.

    Negative or zero quantities break inventory and revenue reports.
    Values that are not numbers are already caught by the type check;
    this rule only looks at rows that DID convert.
    """
    if "quantity" not in df.columns:
        return {
            "name": "Range - quantity > 0",
            "passed": False,
            "message": "quantity column is missing",
            "bad_rows": pd.DataFrame(),
        }

    quantity = coerce_column(df["quantity"], "int")
    convertible = ~quantity.isna()
    invalid = convertible & (quantity <= 0)

    if invalid.any():
        bad_rows = df.loc[invalid, ["quantity"]].copy()
        bad_rows.insert(0, "row_number", bad_rows.index + 2)
        return {
            "name": "Range - quantity > 0",
            "passed": False,
            "message": f"{int(invalid.sum())} row(s) have quantity <= 0",
            "bad_rows": bad_rows,
        }

    return {
        "name": "Range - quantity > 0",
        "passed": True,
        "message": "all convertible quantities are greater than 0",
        "bad_rows": pd.DataFrame(),
    }


def check_allowed_values(df, column, allowed, check_name):
    """Categorical columns should only contain a known set of values.

    Typos like SHIPPD instead of shipped are extremely common in exports
    and will quietly drop rows from a SQL WHERE status = 'shipped' filter.
    Comparison is case-insensitive after stripping spaces.
    """
    if column not in df.columns:
        return {
            "name": check_name,
            "passed": False,
            "message": f"{column} column is missing",
            "bad_rows": pd.DataFrame(),
        }

    normalized = df[column].fillna("").astype(str).str.strip().str.lower()
    allowed_lower = {value.lower() for value in allowed}
    filled = ~is_blank(df[column])
    invalid = filled & ~normalized.isin(allowed_lower)

    if invalid.any():
        bad_rows = df.loc[invalid, [column]].copy()
        bad_rows.insert(0, "row_number", bad_rows.index + 2)
        return {
            "name": check_name,
            "passed": False,
            "message": (
                f"{int(invalid.sum())} unexpected {column} value(s); "
                f"allowed: {', '.join(sorted(allowed))}"
            ),
            "bad_rows": bad_rows,
        }

    return {
        "name": check_name,
        "passed": True,
        "message": f"all filled {column} values are in the allowed list",
        "bad_rows": pd.DataFrame(),
    }


# ---------------------------------------------------------------------------
# 5. Run everything and print a report
# ---------------------------------------------------------------------------
def run_all_checks(df):
    """Return a list of result dicts, one per check, in a stable order."""
    return [
        check_schema_columns(df),
        check_schema_types(df),
        check_nulls(df),
        check_duplicate_rows(df),
        check_duplicate_keys(df),
        check_quantity_positive(df),
        check_allowed_values(df, "status", ALLOWED_STATUSES, "Allowed values - status"),
        check_allowed_values(df, "product", ALLOWED_PRODUCTS, "Allowed values - product"),
    ]


def print_report(results):
    """Print a pass/fail summary, then the bad rows for any failed check."""
    divider = "=" * 64
    print(divider)
    print("DATA QUALITY REPORT")
    print(divider)

    fail_count = 0
    for result in results:
        flag = "PASS" if result["passed"] else "FAIL"
        if not result["passed"]:
            fail_count += 1
        print(f"[{flag}] {result['name']}")
        print(f"       {result['message']}")
        print()

    print(divider)
    print(f"SUMMARY: {len(results) - fail_count} passed, {fail_count} failed")
    print(divider)

    for result in results:
        if result["passed"] or result["bad_rows"].empty:
            continue
        print()
        print(f"--- Details: {result['name']} ---")
        # to_string keeps the table readable in a terminal (no truncated cells).
        print(result["bad_rows"].to_string(index=False))

    return fail_count


def main():
    print(f"Reading: {CSV_PATH}")
    orders = load_orders(CSV_PATH)
    print(f"Loaded {len(orders)} row(s) and {len(orders.columns)} column(s).\n")

    results = run_all_checks(orders)
    fail_count = print_report(results)

    # A non-zero exit code is how scheduled jobs (Airflow, Task Scheduler)
    # notice that quality failed. Running this file by double-clicking still
    # prints the report; the exit code mainly matters in a pipeline.
    if fail_count:
        raise SystemExit(1)


# This standard Python idiom means: "only run main() when this file is
# executed directly, not when another file imports it."
if __name__ == "__main__":
    main()
