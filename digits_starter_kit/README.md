# Schwarz Digits IT KG – Data Engineer Take-Home Assignment
## Starter Kit

Welcome! This repository contains everything you need for the assignment.
Please first read the attached document with the task descriptions.

---

## What is uv?

This project uses **[uv](https://docs.astral.sh/uv/)** as its package manager –
a modern tool written in Rust that combines `pip`, `venv`, and `pip-tools` into a single
command. Setup takes seconds instead of minutes.

| Classic (pip)                     | With uv                   |
|-----------------------------------|---------------------------|
| `python -m venv .venv`            | –                         |
| `source .venv/bin/activate`       | –                         |
| `pip install -r requirements.txt` | `uv sync`                 |
| `python script.py`                | `uv run python script.py` |
| `pytest`                          | `uv run pytest`           |

`uv sync` reads `pyproject.toml`, automatically creates a virtual environment, and
installs all dependencies with exact versions from `uv.lock`.
You **never need to manually activate** the virtual environment.

---

## What is DuckDB?

**[DuckDB](https://duckdb.org/)** is an embedded SQL database – similar to
SQLite, but optimized for analytical queries (OLAP). No server, no Docker,
no configuration. Everything is stored in a single `.duckdb` file.

```python
import duckdb

con = duckdb.connect("digits.duckdb")   # File will be created if it doesn't exist

# Query CSV directly – without creating a table first
con.sql("SELECT * FROM read_csv_auto('data/warehouses.csv') LIMIT 5").show()

# Persistently store table
con.execute("CREATE OR REPLACE TABLE warehouses AS SELECT * FROM read_csv_auto('data/warehouses.csv')")

# Result as pandas DataFrame
df = con.execute("SELECT country, COUNT(*) AS n FROM warehouses GROUP BY country").df()

# Save result as Parquet
con.execute("COPY (SELECT * FROM warehouses) TO 'output/warehouses.parquet' (FORMAT PARQUET)")

con.close()
```

Always start your scripts with `uv run python my_script.py` so that uv
automatically uses the correct virtual environment.

---

## Quickstart

### Prerequisites
- Python 3.9 or newer
- uv (if not already installed):

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart your terminal after installation so that `uv` is in your PATH.

Check if it works:

```bash
uv run python .\hello_uv.py 
```

### 1. Install Dependencies

```bash
uv sync
```

### 2. Generate Sample Data

```bash
uv run python generate_data.py
```

The script will create four CSV files in the `data/` directory:

| File                    | Content                         | Rows   |
|-------------------------|---------------------------------|--------|
| `warehouses.csv`        | Warehouses and transit hubs     | 15     |
| `stores.csv`            | Store master data               | 200    |
| `shipments.csv`         | Shipments                       | 1,400  |
| `events_2024-11-15.csv` | Daily scan events (raw data)    | ~600   |

> The events file contains intentionally built-in data quality issues –
> you can find details about this in the assignment description (Task 2).

### 3. Load Data into DuckDB (for Task 1)

```bash
uv run python load_db.py
```

Afterward, you can write SQL queries against the `warehouses`, `stores`, `shipments`, and `events` tables in `digits.duckdb`.

### Example

```bash
uv run python example.py
```

---

## Adding New Packages

```bash
uv add <package_name>        # e.g.: uv add great-expectations
uv add --dev <package_name>  # only for testing/development
```

---

## Notes

- Please **do not modify** `generate_data.py`. It defines the common data basis.
- PySpark is also permitted: use `uv add pyspark` and run it locally in standalone mode.
- If you have any issues with the setup, please feel free to reach out to us.

Good luck!
