# Data Engineer Take-Home Assignment
**Duration:** 4–6 Hours

## Scenario
In this made-up scenario Lidl coordinates shipments from warehouses to other warehouses and finally to stores.

## Data Basis
4 CSV files located in the `data/` directory (see `README` for setup).

## Submission
Presentation during a live video call (~20 min.). No file upload required.

## Language
German or English

---

### Data Files Overview
All files are located under `data/` and can be generated using `uv run python generate_data.py`.

| File | Content | Description |
| :--- | :--- | :--- |
| `warehouses.csv` | 15 rows | Master data of warehouses and gateway locations |
| `stores.csv` | 200 rows | Store master data including store segments and regional countries |
| `shipments.csv` | 1,400 rows | Completed retail shipments from the last 14 days (`delivered` / `failed`) |
| `events_2024-11-15.csv` | ~600 rows | Raw logistics tracking events from today – 120 new shipments, not yet processed |

---

## Part 1 – Data Model & Analysis (~2 Hours)
**Working Basis:** `warehouses.csv`, `stores.csv`, `shipments.csv`

### 1.1 Data Model
Design a dimensional data model (Star Schema or Snowflake) that can answer the following business questions:
* Average delivery time (`created_at` to `completed_at`) per store segment
* Error rate (`failed` / total) per warehouse and month
* Shipment volume per country and week

Briefly describe your model—a tabular overview or an ERD (Entity-Relationship Diagram) sketch is sufficient.

### 1.2 SQL Queries
Write SQL queries for the following analyses. Use DuckDB (`digits.duckdb`) for this purpose.

1. **Top 5 warehouses by error rate** over the entire period. Only consider warehouses with at least 50 shipments.
2. **Average delivery time in hours** per store segment, sorted in descending order.
3. **Weekly shipment volume** (number of shipments) for the last 14 days, split by status (`delivered` / `failed`).

*Note: The queries should run directly against `shipments.csv` or `digits.duckdb`. Place your `.sql` files in the `sql/` directory. Ensure clean SQL formatting following modern standards.*

---

## Part 2 – Pipeline & Incremental Load (~2.5 Hours)
**Working Basis:** `events_2024-11-15.csv` contains the raw data from today—120 new shipments that are not yet included in `shipments.csv`.

### 2.1 Data Cleaning
The events file contains intentionally built-in quality issues. Write a Python script that:
* Discards rows with a missing `shipment_id` or `warehouse_nr` and logs them into `rejected_events.csv` (including the error reason).
* Removes duplicates based on `event_id`—keep the entry with the latest `occurred_at`.
* Standardizes `occurred_at` into a uniform format (ISO 8601: `YYYY-MM-DD HH:MM:SS`).
* Normalizes `event_type` (remove whitespaces, convert to lowercase).

### 2.2 Incremental Load
Derive new shipment entries from the cleaned events and insert them into the existing shipments table:
* Each unique `shipment_id` in the events corresponds to a new shipment (there is no overlap with `shipments.csv`).
* Determine the `origin_warehouse_nr` (warehouse of the first `picked_up` event) and `dest_warehouse_nr` (warehouse of the last recorded event).
* Determine the final status from the last event (`delivered` or `failed`).
* Set `created_at` to the earliest `occurred_at` and `completed_at` to the latest `occurred_at` of that shipment.
* Insert the new rows into the `shipments` table inside DuckDB.

### 2.3 Verification
Run your SQL queries from Part 1 again after completing the data load. The results should now include the 120 new shipments.

*Note: Write at least two unit tests for critical parts of your cleaning logic (e.g., using `pytest`).*

---

## Bonus (Optional)
These tasks are voluntary. They can improve the overall impression of your submission, but will not penalize you if left uncompleted.

* Additionally save the cleaned events as a Parquet file, partitioned by `year / month / day`.
* Make the pipeline idempotent—running it multiple times with the same data should produce the exact same result.
* Briefly describe how you would orchestrate this pipeline in a production environment (e.g., Airflow, dbt, or another tool of your choice).

---

## Evaluation Criteria
We are not looking for absolute perfection, but rather want to understand your thought process. We focus on:

| Criterion | What We Look For | Weight |
| :--- | :--- | :--- |
| **Correctness** | Do the SQL queries and pipeline deliver the expected results? | 30% |
| **Code Quality** | Readability, code structure, and appropriate commenting | 25% |
| **Data Model** | Meaningful schema, clear naming conventions, and justified architectural choices | 20% |
| **Robustness** | Error handling, edge cases, and automated testing | 15% |
| **Documentation** | Clear `README`, architectural justifications, and notes on what was left out and why | 10% |

---

## General Instructions
* **Do not modify `generate_data.py`**—it defines the standardized baseline for all candidates.
* External libraries are permitted. You can add new packages using `uv add <package>`.
* If you cannot fully complete a task, document how you would have approached it.
* Please do not use AI tools for code implementation. Researching concepts and reading documentation is completely acceptable.
* You will present your solution live during a video call—ensure that your code runs locally on your machine.

**Good luck! We look forward to discussing your solution.**