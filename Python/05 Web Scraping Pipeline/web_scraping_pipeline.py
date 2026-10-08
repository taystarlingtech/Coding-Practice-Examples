"""
Web Scraping Pipeline (project 05)
==================================

What this file does
-------------------
A scraping pipeline pulls data out of web pages and stores it as a clean
table. The three steps match a tiny ETL job:

  1. Extract  - download HTML from a site that allows practice scraping
  2. Transform - parse quotes with BeautifulSoup, then tidy them with Pandas
  3. Load     - write a CSV you can open in Excel or feed to project 04

Why this site
-------------
https://quotes.toscrape.com/ is a public practice site made for learning
scrapers. Scraping a random company's production site without permission
is a bad idea (ToS, robots.txt, and layout that can change without notice).

There is already a Scrapy tutorial folder in this Python directory.
This project uses requests + BeautifulSoup instead, so every step is
visible in one file - closer to the infographic (BeautifulSoup, Pandas).

How to run
----------
    python web_scraping_pipeline.py

Needs: requests, beautifulsoup4, pandas
The CSV is written next to this script, so the working directory does
not matter.
"""

import time
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup


# ---------------------------------------------------------------------------
# 1. Settings - keep the "where and how politely" rules in one place
# ---------------------------------------------------------------------------
# A real User-Agent is more honest than pretending to be Chrome, and many
# practice sites still accept it. Identifying the script also makes logs
# easier to read if a site owner ever checks.
BASE_URL = "https://quotes.toscrape.com/"
USER_AGENT = (
    "TayStarlingPortfolio/1.0 "
    "(educational scraper for quotes.toscrape.com)"
)

# Pause between page requests. Even a practice site should not be hammered.
# 0.5 seconds is plenty here; production jobs often wait 1-3 seconds.
REQUEST_DELAY_SECONDS = 0.5

# Stop after this many pages so a bug in the "next" link cannot loop forever.
# quotes.toscrape.com currently has 10 pages of 10 quotes.
MAX_PAGES = 10

OUTPUT_CSV = Path(__file__).resolve().parent / "quotes.csv"


# ---------------------------------------------------------------------------
# 2. Extract - download one HTML page
# ---------------------------------------------------------------------------
def fetch_page(url):
    """GET a URL and return the response text.

    timeout=15 stops the script from hanging if the network stalls.
    raise_for_status() turns HTTP 404/500 into an exception instead of
    handing BeautifulSoup an error page to parse as if it were quotes.
    """
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=15,
    )
    response.raise_for_status()
    return response.text


# ---------------------------------------------------------------------------
# 3. Parse - turn HTML into a list of dictionaries
# ---------------------------------------------------------------------------
def parse_quotes(html):
    """Find every quote card on the page.

    Open https://quotes.toscrape.com/ and use View Source (or DevTools)
    to see the pattern this function depends on:

        <div class="quote">
          <span class="text">"The quote."</span>
          <small class="author">Author Name</small>
          <a class="tag">tag-one</a>
          ...
        </div>

    If the site redesigns those class names, this function is what breaks.
    That fragility is why APIs are usually a better source than HTML.
    """
    soup = BeautifulSoup(html, "html.parser")
    rows = []

    for card in soup.select("div.quote"):
        text_el = card.select_one("span.text")
        author_el = card.select_one("small.author")
        tag_els = card.select("a.tag")

        # skip a malformed card rather than crashing the whole run
        if text_el is None or author_el is None:
            continue

        raw_text = text_el.get_text()
        # The site wraps quotes in Unicode curly quotes (“ ... ”).
        # Strip those plus leftover whitespace so the CSV is plain text.
        cleaned_text = raw_text.strip().strip("“”\"'")

        rows.append(
            {
                "quote": cleaned_text,
                "author": author_el.get_text(strip=True),
                # Join tags with a pipe so one CSV cell can hold several tags
                # without colliding with the comma that separates columns.
                "tags": "|".join(tag.get_text(strip=True) for tag in tag_els),
            }
        )

    return rows


def find_next_page(html, current_url):
    """Return the full URL of the Next link, or None on the last page.

    urljoin() turns a relative href like "/page/2/" into
    "https://quotes.toscrape.com/page/2/" using the page we are on.
    """
    soup = BeautifulSoup(html, "html.parser")
    next_link = soup.select_one("li.next a")
    if next_link is None or not next_link.get("href"):
        return None
    return urljoin(current_url, next_link["href"])


# ---------------------------------------------------------------------------
# 4. Crawl - walk pagination until there is no Next (or MAX_PAGES)
# ---------------------------------------------------------------------------
def scrape_all_quotes():
    """Visit page 1, then follow Next links. Return a list of row dicts."""
    url = BASE_URL
    all_rows = []

    for page_number in range(1, MAX_PAGES + 1):
        print(f"Fetching page {page_number}: {url}")
        html = fetch_page(url)
        page_rows = parse_quotes(html)
        print(f"  parsed {len(page_rows)} quote(s)")
        all_rows.extend(page_rows)

        next_url = find_next_page(html, url)
        if next_url is None:
            print("  no Next link - reached the last page")
            break

        url = next_url
        # Sleep after a successful fetch so we do not burst requests.
        time.sleep(REQUEST_DELAY_SECONDS)

    return all_rows


# ---------------------------------------------------------------------------
# 5. Transform - Pandas cleanup before writing the file
# ---------------------------------------------------------------------------
def clean_quotes(rows):
    """Build a DataFrame and apply the same kind of tidy-up as reporting exports.

    Dropping exact duplicate quotes matters because a pagination bug can
    scrape the same page twice. Sorting makes the CSV stable from run to run.
    """
    df = pd.DataFrame(rows, columns=["quote", "author", "tags"])

    if df.empty:
        raise ValueError("No quotes were parsed. The site layout may have changed.")

    df["quote"] = df["quote"].str.strip()
    df["author"] = df["author"].str.strip()
    df["tags"] = df["tags"].fillna("").str.strip()

    before = len(df)
    df = df.drop_duplicates(subset=["quote", "author"]).reset_index(drop=True)
    dropped = before - len(df)
    if dropped:
        print(f"Removed {dropped} duplicate row(s).")

    df = df.sort_values(["author", "quote"], kind="mergesort").reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# 6. Load - write the clean table
# ---------------------------------------------------------------------------
def save_csv(df, path):
    """Write UTF-8 CSV. encoding='utf-8-sig' helps Excel on Windows."""
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"Wrote {len(df)} row(s) to {path}")


def main():
    print(f"Starting scrape of {BASE_URL}")
    rows = scrape_all_quotes()
    print(f"Raw rows collected: {len(rows)}")

    quotes = clean_quotes(rows)
    print("\nPreview (first 5 rows):")
    print(quotes.head().to_string(index=False))
    print("\nQuotes per author (top 5):")
    print(quotes["author"].value_counts().head().to_string())

    save_csv(quotes, OUTPUT_CSV)


if __name__ == "__main__":
    main()
