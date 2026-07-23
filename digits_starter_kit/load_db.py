"""
load_db.py – Loads all raw CSV data into a local DuckDB database.

Usage:
    uv run python load_db.py
"""

import duckdb
import os

DB_FILE = "digits.duckdb"
DATA_DIR = "data"

def main():
    if not os.path.isdir(DATA_DIR):
        print(f"Directory '{DATA_DIR}/' not found.")
        print("Please run first: uv run python generate_data.py")
        raise SystemExit(1)

    con = duckdb.connect(DB_FILE)

    tables = {
        "warehouses": f"{DATA_DIR}/warehouses.csv",
        "stores":     f"{DATA_DIR}/stores.csv",
        "shipments":  f"{DATA_DIR}/shipments.csv",
        "events":     f"{DATA_DIR}/events_2024-11-15.csv",
    }

    for table, path in tables.items():
        con.execute(
            f"CREATE OR REPLACE TABLE {table} AS "
            f"SELECT * FROM read_csv_auto('{path}')"
        )
        count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:<12} loaded   ({count:>6} rows)")

    print()
    print(f"Database ready: {DB_FILE}")
    print()
    print("Quick test:")
    con.sql("SHOW TABLES").show()

    con.close()


if __name__ == "__main__":
    main()
