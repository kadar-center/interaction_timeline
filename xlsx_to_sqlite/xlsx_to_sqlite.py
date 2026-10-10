"""
xlsx_to_sqlite.py

Reads timeline.xlsx and produces a SQLite database matching the new
timeline workbook export format:

  items  - core event data plus named text/content columns
  links  - linked item pairs, unpivoted from link1..link4

Usage:
    python xlsx_to_sqlite.py [path/to/timeline.xlsx] [output.db]

Defaults:
    input  -> timeline.xlsx
    output -> timeline_data.db
"""

from pathlib import Path
import sqlite3
import sys
import warnings

import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")


ITEM_COLUMNS = [
    "id",
    "era",
    "year",
    "type",
    "hebrew_header",
    "english_header",
    "about_item",
    "about_author",
    "text_character",
    "text_historical",
    "text_quote",
    "text_term",
]

LINK_COLUMNS = ["link1", "link2", "link3", "link4"]
REQUIRED_COLUMNS = ITEM_COLUMNS + LINK_COLUMNS

CREATE_SCHEMA_SQL = """
CREATE TABLE items (
    id                    INT,
    era                   TEXT,
    year                  INT,
    type                  TEXT,
    hebrew_header         TEXT,
    english_header        TEXT,
    about_item            TEXT,
    about_author          TEXT,
    text_character        TEXT,
    text_historical       TEXT,
    text_quote            TEXT,
    text_term             TEXT
);

CREATE TABLE links (
    id        INT,
    target_id INT
);
"""


def require_columns(df):
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(
            "Missing required columns in Sheet1: " + ", ".join(missing)
        )


def load_workbook_data(xlsx_path):
    df = pd.read_excel(xlsx_path, sheet_name="Sheet1")
    df = df.drop(columns=["Unnamed: 0"], errors="ignore")
    require_columns(df)

    # Ignore trailing workbook rows only if Excel exposes them as fully blank.
    df = df.dropna(how="all").copy()
    return df


def build_items(df):
    items = df[ITEM_COLUMNS].copy()
    items["id"] = items["id"].astype(int)
    items["year"] = items["year"].astype(int)
    return items


def coerce_link_id(value, source_id, column):
    if pd.isna(value):
        return None

    numeric_value = float(value)
    if not numeric_value.is_integer():
        raise ValueError(
            f"Invalid link target {value!r} in {column} for item {source_id}"
        )
    return int(numeric_value)


def build_links(df):
    valid_item_ids = set(df["id"].astype(int))
    link_rows = []

    for _, row in df[["id"] + LINK_COLUMNS].iterrows():
        source_id = int(row["id"])
        for column in LINK_COLUMNS:
            target_id = coerce_link_id(row[column], source_id, column)
            if target_id is None:
                continue
            if target_id not in valid_item_ids:
                raise ValueError(
                    f"Invalid link target {target_id} in {column} for item {source_id}"
                )
            link_rows.append({"id": source_id, "target_id": target_id})

    return pd.DataFrame(link_rows, columns=["id", "target_id"])


def write_database(db_path, items, links):
    with sqlite3.connect(db_path) as con:
        con.executescript(CREATE_SCHEMA_SQL)
        items.to_sql("items", con, if_exists="append", index=False)
        links.to_sql("links", con, if_exists="append", index=False)


def main():
    xlsx_path = Path(sys.argv[1] if len(sys.argv) > 1 else "timeline.xlsx")
    db_path = Path(sys.argv[2] if len(sys.argv) > 2 else "timeline_data.db")

    df = load_workbook_data(xlsx_path)
    items = build_items(df)
    links = build_links(df)
    write_database(db_path, items, links)

    print(f"Done -> {db_path}")
    print(f"  items : {len(items)} rows")
    print(f"  links : {len(links)} rows")


if __name__ == "__main__":
    main()
