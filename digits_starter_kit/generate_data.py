"""
Schwarz Digits – Test Data Generator
====================================
Generates realistic sample data for the Data Engineer take-home assignment.

Files:
  data/warehouses.csv        – fixed, 15 European warehouses (master data)
  data/stores.csv            – fixed, 200 stores (master data)
  data/shipments.csv         – 14 days history, already processed
  data/events_2024-11-15.csv – today's raw data, not yet processed

Usage:
    uv run python generate_data.py
    uv run python generate_data.py --seed 99
"""

import argparse
import csv
import os
import random
from datetime import datetime, timedelta

# ── Configuration ─────────────────────────────────────────────────────────────
SEED = 42
N_STORES = 200
N_SHIPMENTS_HIST = 1_400  # Shipments from the last 14 days (already processed)
N_SHIPMENTS_TODAY = 120  # New shipments from today (still raw in events)
TODAY = datetime(2024, 11, 14)
OUTPUT_DIR = "data"

parser = argparse.ArgumentParser()
parser.add_argument("--seed", type=int, default=SEED)
args = parser.parse_args()
random.seed(args.seed)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── 1. Warehouses (fixed) ─────────────────────────────────────────────────────
WAREHOUSES = [
    ("WH-BER", "Berlin", "DE", "gateway"),
    ("WH-HAM", "Hamburg", "DE", "regional"),
    ("WH-MUC", "Munich", "DE", "regional"),
    ("WH-CGN", "Cologne", "DE", "regional"),
    ("WH-FRA", "Frankfurt", "DE", "gateway"),
    ("WH-AMS", "Amsterdam", "NL", "gateway"),
    ("WH-CDG", "Paris", "FR", "gateway"),
    ("WH-MAD", "Madrid", "ES", "regional"),
    ("WH-MXP", "Milan", "IT", "regional"),
    ("WH-WAW", "Warsaw", "PL", "regional"),
    ("WH-VIE", "Vienna", "AT", "regional"),
    ("WH-ZRH", "Zurich", "CH", "regional"),
    ("WH-BCN", "Barcelona", "ES", "regional"),
    ("WH-PRG", "Prague", "CZ", "local"),
    ("WH-BRU", "Brussels", "BE", "local"),
]
WAREHOUSE_IDS = [w[0] for w in WAREHOUSES]

with open(f"{OUTPUT_DIR}/warehouses.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["warehouse_nr", "city", "country", "warehouse_type"])
    w.writerows(WAREHOUSES)

print(f"  warehouses.csv       ({len(WAREHOUSES)} rows, fixed)")

# ── 2. Stores (fixed) ─────────────────────────────────────────────────────────
# Segments represent physical store format layouts
SEGMENTS = ["Standard", "Compact", "Hypermarket"]
COUNTRIES = ["DE", "DE", "DE", "NL", "FR", "AT", "CH", "PL", "ES", "IT"]

# Store names updated strictly to Lidl store designations
STORE_NAMES = [
    "Lidl Store",
    "Lidl Filiale",
    "Lidl Supermarkt",
    "Lidl Express",
    "Lidl Center",
]

stores = [
    {
        "store_id": f"STR{i:04d}",
        "name": random.choice(STORE_NAMES) + f" #{i}",
        "segment": random.choice(SEGMENTS),
        "country": random.choice(COUNTRIES),
    }
    for i in range(1, N_STORES + 1)
]
STR_IDS = [s["store_id"] for s in stores]

with open(f"{OUTPUT_DIR}/stores.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["store_id", "name", "segment", "country"])
    w.writeheader()
    w.writerows(stores)

print(f"  stores.csv           ({len(stores)} rows, fixed)")

# ── 3. Shipments – 14-day history (already processed) ────────────────────
#
# No event log for these shipments. Status and timestamps are set
# directly – this represents the already processed, clean state.

shipments = []
for i in range(1, N_SHIPMENTS_HIST + 1):
    origin, dest = random.sample(WAREHOUSE_IDS, 2)
    # created_at: sometime in the last 14 days (not today)
    created_at = TODAY - timedelta(
        days=random.randint(1, 14),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )
    # completed_at: 6–48 hours after created_at
    completed_at = created_at + timedelta(hours=random.uniform(6, 48))
    # Status: 85% delivered, 15% failed
    status = "delivered" if random.random() < 0.85 else "failed"

    shipments.append(
        {
            "shipment_id": f"SHP{i:05d}",
            "store_id": random.choice(STR_IDS),
            "origin_warehouse_nr": origin,
            "dest_warehouse_nr": dest,
            "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "completed_at": completed_at.strftime("%Y-%m-%d %H:%M:%S"),
            "status": status,
        }
    )

with open(f"{OUTPUT_DIR}/shipments.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(
        f,
        fieldnames=[
            "shipment_id",
            "store_id",
            "origin_warehouse_nr",
            "dest_warehouse_nr",
            "created_at",
            "completed_at",
            "status",
        ],
    )
    w.writeheader()
    w.writerows(shipments)

print(f"  shipments.csv        ({len(shipments)} rows, 14-day history)")

# ── 4. Events – today's raw data (not yet processed) ────────────────────
#
# Each new shipment gets a coherent event chain with strictly
# ascending timestamps. All warehouse_nrs are from WAREHOUSE_IDS.
# No shipment_id overlaps with shipments.csv.

EVENT_FIELDS = ["event_id", "shipment_id", "warehouse_nr", "event_type", "occurred_at"]

events = []
evt_counter = 1

# Start index for shipment_ids directly after history
shp_counter = N_SHIPMENTS_HIST + 1


def next_evt(shipment_id, warehouse_nr, event_type, ts):
    global evt_counter
    e = {
        "event_id": f"EVT{evt_counter:06d}",
        "shipment_id": shipment_id,
        "warehouse_nr": warehouse_nr,
        "event_type": event_type,
        "occurred_at": ts.strftime("%Y-%m-%d %H:%M:%S"),
    }
    evt_counter += 1
    return e


new_shipment_ids = set()

for _ in range(N_SHIPMENTS_TODAY):
    sid = f"SHP{shp_counter:05d}"
    shp_counter += 1
    new_shipment_ids.add(sid)

    origin, dest = random.sample(WAREHOUSE_IDS, 2)
    # Shipment was created and picked up early today
    t = TODAY + timedelta(
        days=1, hours=random.uniform(0, 8), minutes=random.randint(0, 59)
    )

    chain = []

    # picked_up at origin warehouse
    chain.append(next_evt(sid, origin, "picked_up", t))
    t += timedelta(hours=random.uniform(0.5, 2))

    # 0–2 intermediate warehouses
    n_intermediate = random.choices([0, 1, 2], weights=[0.4, 0.4, 0.2])[0]
    intermediate_warehouses = random.sample(
        [w for w in WAREHOUSE_IDS if w not in (origin, dest)], n_intermediate
    )

    for warehouse in intermediate_warehouses:
        chain.append(next_evt(sid, warehouse, "arrived", t))
        t += timedelta(hours=random.uniform(0.5, 2))
        chain.append(next_evt(sid, warehouse, "departed", t))
        t += timedelta(hours=random.uniform(1, 4))

    # Arrival at destination warehouse
    chain.append(next_evt(sid, dest, "arrived", t))
    t += timedelta(hours=random.uniform(0.5, 2))

    # Completion: 85% delivered, 15% failed
    outcome = "delivered" if random.random() < 0.85 else "failed"
    chain.append(next_evt(sid, dest, outcome, t))

    events.extend(chain)

# Inject data quality issues
# ─────────────────────────────────
# We keep clean copies before injecting errors,
# so that quality issues only affect the raw file.

clean_events = [e.copy() for e in events]

# Issue 1: ~3% missing shipment_id
for e in random.sample(events, int(len(events) * 0.03)):
    e["shipment_id"] = ""

# Issue 2: ~2% missing warehouse_nr
for e in random.sample(events, int(len(events) * 0.02)):
    e["warehouse_nr"] = ""

# Issue 3: ~5% duplicates (same event_id, occurred_at +1-10 sec.)
# Only duplicate the last event per shipment to avoid breaking the
# ascending timestamp order within the chain.
last_per_shipment = {}
for e in clean_events:
    last_per_shipment[e["shipment_id"]] = e  # last event wins
dupe_pool = list(last_per_shipment.values())
n_dupes = int(len(events) * 0.05)
dupes = []
for e in random.sample(dupe_pool, min(n_dupes, len(dupe_pool))):
    d = e.copy()
    orig_ts = datetime.strptime(d["occurred_at"], "%Y-%m-%d %H:%M:%S")
    d["occurred_at"] = (orig_ts + timedelta(seconds=random.randint(1, 10))).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    dupes.append(d)
events.extend(dupes)

# Issue 4: ~4% alternative date format (DD.MM.YYYY HH:MM)
for e in random.sample(events, int(len(events) * 0.04)):
    try:
        ts = datetime.strptime(e["occurred_at"], "%Y-%m-%d %H:%M:%S")
        e["occurred_at"] = ts.strftime("%d.%m.%Y %H:%M")
    except ValueError:
        pass

# Issue 5: ~3% event_type with mixed casing or trailing spaces
for e in random.sample(events, int(len(events) * 0.03)):
    choice = random.randint(0, 2)
    if choice == 0:
        e["event_type"] = e["event_type"].upper()
    elif choice == 1:
        e["event_type"] = "  " + e["event_type"]
    else:
        e["event_type"] = e["event_type"] + "  "

random.shuffle(events)

with open(
    f"{OUTPUT_DIR}/events_2024-11-15.csv", "w", newline="", encoding="utf-8"
) as f:
    w = csv.DictWriter(f, fieldnames=EVENT_FIELDS)
    w.writeheader()
    w.writerows(events)

# ── Summary ───────────────────────────────────────────────────────────
n_miss_shp = sum(1 for e in events if not e["shipment_id"])
n_miss_wh = sum(1 for e in events if not e["warehouse_nr"])
seen, n_dup = set(), 0
for e in events:
    if e["event_id"] in seen:
        n_dup += 1
    seen.add(e["event_id"])

print(
    f"  events_2024-11-15.csv ({len(events)} rows, {N_SHIPMENTS_TODAY} new shipments)"
)
print()
print("  Built-in quality issues in events_2024-11-15.csv:")
print(f"    missing shipment_id      : {n_miss_shp} rows")
print(f"    missing warehouse_nr     : {n_miss_wh} rows")
print(f"    duplicates (event_id)    : {n_dup} rows")
print(f"    alternative date format  : ~{int(len(events) * 0.04)} rows")
print(f"    casing/whitespace errors : ~{int(len(events) * 0.03)} rows")
print()
print(
    f"  New shipment_ids (not in shipments.csv): SHP{N_SHIPMENTS_HIST + 1:05d} – SHP{shp_counter - 1:05d}"
)
print()
print(f"All files have been saved to ./{OUTPUT_DIR}/")
