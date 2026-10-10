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
