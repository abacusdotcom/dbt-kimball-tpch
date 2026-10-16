"""Change some customers in the source so the next `dbt snapshot` records history.

Two business events, each stamped with its own effective date:
  segment  1995-07-01  every 50th customer moves to the next market segment
  nation   1996-01-01  every 75th customer relocates to the next nation

Run them one at a time with a `dbt build` in between to capture both versions:
    python scripts/simulate_changes.py --event segment && dbt build --profiles-dir .
    python scripts/simulate_changes.py --event nation  && dbt build --profiles-dir .

Customers hit by both (every 150th) then end up with three versions. Run both
events before a single build instead and the middle version is never recorded:
a snapshot only sees the state of the source at the moment it runs.

Safe to run more than once: rows already changed are skipped.
"""
import argparse

import duckdb

EVENTS = {
    "segment": """
        UPDATE raw.customer
        SET c_mktsegment = CASE c_mktsegment
                WHEN 'AUTOMOBILE' THEN 'BUILDING'
                WHEN 'BUILDING'   THEN 'FURNITURE'
                WHEN 'FURNITURE'  THEN 'HOUSEHOLD'
                WHEN 'HOUSEHOLD'  THEN 'MACHINERY'
                ELSE 'AUTOMOBILE'
            END,
            updated_at = TIMESTAMP '1995-07-01'
        WHERE c_custkey % 50 = 0
          AND updated_at < TIMESTAMP '1995-07-01'
    """,
    "nation": """
        UPDATE raw.customer
        SET c_nationkey = (c_nationkey + 1) % 25,
            updated_at = TIMESTAMP '1996-01-01'
        WHERE c_custkey % 75 = 0
          AND updated_at < TIMESTAMP '1996-01-01'
    """,
}

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("--event", choices=[*EVENTS, "all"], default="all")
args = parser.parse_args()

con = duckdb.connect("tpch.duckdb")
for name in (EVENTS if args.event == "all" else [args.event]):
    changed = con.execute(EVENTS[name]).fetchone()[0]
    print(f"{name}: {changed:,} customers changed")
con.close()
print("Now run: dbt build --profiles-dir .")
