"""
example.py – Minimal example: shows that the Starter Kit is working.

Covers all three task areas:
  1. SQL / DuckDB query        (Task 1)
  2. Simple data transformation (Task 2)
  3. Parquet export             (Task 2/3)

Usage:
    uv run python example.py
"""

import os
import duckdb

DB_FILE = "digits.duckdb"
OUT_DIR = "output_example"
os.makedirs(OUT_DIR, exist_ok=True)

con = duckdb.connect(DB_FILE)

print("=" * 55)
print("  Schwarz Digits Starter Kit – Example Output")
print("=" * 55)

# ── 1. SQL Query: Load a mock SQL query from an external file ───────────
print("Executing mock SQL query loaded from file:")

script_dir = os.path.dirname(os.path.abspath(__file__))
sql_file_path = os.path.join(script_dir, "sql", "mock_query.sql")

# Load and execute the SQL file
with open(sql_file_path, "r", encoding="utf-8") as f:
    query = f.read()

print(f"--- Query from {sql_file_path} ---")
df_result = con.execute(query).df()
print(df_result.to_string(index=False))

con.close()
