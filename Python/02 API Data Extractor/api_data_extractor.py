"""
API Data Extractor (project 02)
===============================

What this file does
-------------------
Pull JSON from a public REST API, keep the raw payload, then flatten it
into a table. Saving raw JSON first is the "landing zone" idea: if your
parser breaks next month, you can still replay yesterday's file.

Decisions baked into this version
---------------------------------
* JSONPlaceholder (jsonplaceholder.typicode.com)
  No API key, no billing, built for tutorials. A production extractor
  would swap BASE_URL and the field list; the retry / pagination /
  raw-save pattern stays the same.

* Save raw JSON before flattening
  Nested JSON is easy to lose when you immediately pick columns.
  raw/page_01.json is the audit copy. posts.csv is the working copy.

* Pagination with _page / _limit
  Real APIs almost never return the whole dataset in one response.
  JSONPlaceholder supports these query params, so we practice the loop.

* Retries with backoff, timeout, User-Agent
  Same politeness rules as the scraping project. Timeouts stop a hung
  run; retries absorb a single blip without crashing the job.

This extractor does NOT load SQL (project 01) and does NOT upsert
(project 07). It stops at a clean CSV of extracted records.

How to run
----------
    python api_data_extractor.py

Needs: requests, pandas
Writes raw/*.json and posts.csv next to this script.
"""

import json
import time
from pathlib import Path

import pandas as pd
import requests


SCRIPT_DIR = Path(__file__).resolve().parent
RAW_DIR = SCRIPT_DIR / "raw"
OUTPUT_CSV = SCRIPT_DIR / "posts.csv"

BASE_URL = "https://jsonplaceholder.typicode.com/posts"
USER_AGENT = "TayStarlingPortfolio/1.0 (educational API extractor)"
PAGE_SIZE = 20
MAX_PAGES = 10
REQUEST_DELAY_SECONDS = 0.25
MAX_RETRIES = 3
TIMEOUT_SECONDS = 15


def fetch_page(page_number):
    """GET one page of posts. Retry a few times on network / 5xx errors.

    4xx errors (except 429) are not retried: they usually mean the URL
    or params are wrong, and waiting will not fix that.
    """
    params = {"_page": page_number, "_limit": PAGE_SIZE}
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                BASE_URL,
                params=params,
                headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
                timeout=TIMEOUT_SECONDS,
            )
            if response.status_code == 429 or response.status_code >= 500:
                # rate-limited or server error: worth retrying
                response.raise_for_status()
            response.raise_for_status()
            return response.json()
        except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as error:
            last_error = error
            wait = 2 ** (attempt - 1)
            print(f"  attempt {attempt} failed ({error}); waiting {wait}s")
            time.sleep(wait)

    raise RuntimeError(f"Failed to fetch page {page_number} after {MAX_RETRIES} tries") from last_error


def save_raw(page_number, payload):
    """Write the untouched JSON list for this page."""
    RAW_DIR.mkdir(exist_ok=True)
    path = RAW_DIR / f"page_{page_number:02d}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def flatten_posts(posts):
    """Turn API dicts into a rectangular table.

    JSONPlaceholder posts look like:
        {"userId": 1, "id": 1, "title": "...", "body": "..."}

    We rename id -> post_id so it is obvious this is the business key,
    not a dataframe index.
    """
    rows = []
    for post in posts:
        rows.append(
            {
                "post_id": post.get("id"),
                "user_id": post.get("userId"),
                "title": (post.get("title") or "").strip(),
                "body": (post.get("body") or "").replace("\n", " ").strip(),
            }
        )
    return rows


def extract_all():
    """Walk pages until an empty page (or MAX_PAGES)."""
    RAW_DIR.mkdir(exist_ok=True)
    all_rows = []

    for page_number in range(1, MAX_PAGES + 1):
        print(f"Fetching page {page_number}")
        payload = fetch_page(page_number)
        raw_path = save_raw(page_number, payload)
        print(f"  saved {len(payload)} record(s) to {raw_path.name}")

        if not payload:
            print("  empty page - done")
            break

        all_rows.extend(flatten_posts(payload))
        time.sleep(REQUEST_DELAY_SECONDS)

    return all_rows


def main():
    print(f"Extracting from {BASE_URL}")
    rows = extract_all()
    if not rows:
        raise ValueError("API returned no posts. Check the URL or pagination params.")

    df = pd.DataFrame(rows, columns=["post_id", "user_id", "title", "body"])
    before = len(df)
    df = df.drop_duplicates(subset=["post_id"]).sort_values("post_id").reset_index(drop=True)
    if len(df) != before:
        print(f"Removed {before - len(df)} duplicate post_id(s).")

    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"\nWrote {len(df)} row(s) to {OUTPUT_CSV.name}")
    print("\nPreview:")
    print(df.head().to_string(index=False))
    print("\nPosts per user_id (top 5):")
    print(df["user_id"].value_counts().head().to_string())
    print("\nRaw JSON is in the raw/ folder. Load that CSV with project 01, or upsert with project 07.")


if __name__ == "__main__":
    main()
