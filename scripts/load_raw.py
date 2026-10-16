"""Load TPC-H sample data into the raw schema of tpch.duckdb.

Starts from a clean database file every time, because the dbt snapshot
history lives in the same file and must be rebuilt alongside the raw data.

Usage:
    python scripts/load_raw.py                 # TPC-H via DuckDB's tpch extension, scale factor 0.1
    python scripts/load_raw.py --sf 1          # bigger dataset (~6M order lines)
    python scripts/load_raw.py --synthetic     # no extension download needed (offline / locked-down networks)

If the tpch extension can't be downloaded, the script falls back to the
synthetic generator automatically. Both produce the same tables and columns.
"""
import argparse
import os

import duckdb

DB_PATH = "tpch.duckdb"


def load_tpch(con, sf):
    con.execute("INSTALL tpch; LOAD tpch;")
    con.execute(f"CALL dbgen(sf = {sf}, schema = 'raw')")


def load_synthetic(con, sf):
    """TPC-H-shaped data generated with plain SQL, same columns as dbgen."""
    n_cust = max(int(150_000 * sf), 500)
    n_part = max(int(200_000 * sf), 500)
    n_supp = max(int(10_000 * sf), 50)
    n_orders = max(int(1_500_000 * sf), 5_000)
    con.execute("SELECT setseed(0.42)")
    con.execute("""
        CREATE TABLE raw.region AS
        SELECT * FROM (VALUES
            (0, 'AFRICA', ''), (1, 'AMERICA', ''), (2, 'ASIA', ''),
            (3, 'EUROPE', ''), (4, 'MIDDLE EAST', '')
        ) t(r_regionkey, r_name, r_comment)
    """)
    con.execute("""
        CREATE TABLE raw.nation AS
        SELECT * FROM (VALUES
            (0,'ALGERIA',0),(1,'ARGENTINA',1),(2,'BRAZIL',1),(3,'CANADA',1),(4,'EGYPT',4),
            (5,'ETHIOPIA',0),(6,'FRANCE',3),(7,'GERMANY',3),(8,'INDIA',2),(9,'INDONESIA',2),
            (10,'IRAN',4),(11,'IRAQ',4),(12,'JAPAN',2),(13,'JORDAN',4),(14,'KENYA',0),
            (15,'MOROCCO',0),(16,'MOZAMBIQUE',0),(17,'PERU',1),(18,'CHINA',2),(19,'ROMANIA',3),
            (20,'SAUDI ARABIA',4),(21,'VIETNAM',2),(22,'RUSSIA',3),(23,'UNITED KINGDOM',3),
            (24,'UNITED STATES',1)
        ) t(n_nationkey, n_name, n_regionkey)
    """)
    con.execute("ALTER TABLE raw.nation ADD COLUMN n_comment VARCHAR DEFAULT ''")
    con.execute(f"""
        CREATE TABLE raw.customer AS
        SELECT
            i AS c_custkey,
            'Customer#' || lpad(i::VARCHAR, 9, '0') AS c_name,
            'Address ' || i AS c_address,
            (i * 7) % 25 AS c_nationkey,
            '10-' || lpad((i % 1000)::VARCHAR, 3, '0') || '-555-0100' AS c_phone,
            round(random() * 10999.99 - 999.99, 2)::DECIMAL(15,2) AS c_acctbal,
            (['AUTOMOBILE','BUILDING','FURNITURE','HOUSEHOLD','MACHINERY'])[(i % 5) + 1] AS c_mktsegment,
            '' AS c_comment
        FROM range(1, {n_cust} + 1) r(i)
    """)
    con.execute(f"""
        CREATE TABLE raw.supplier AS
        SELECT
            i AS s_suppkey,
            'Supplier#' || lpad(i::VARCHAR, 9, '0') AS s_name,
            'Address ' || i AS s_address,
            (i * 3) % 25 AS s_nationkey,
            '20-555-0100' AS s_phone,
            round(random() * 10999.99 - 999.99, 2)::DECIMAL(15,2) AS s_acctbal,
            '' AS s_comment
        FROM range(1, {n_supp} + 1) r(i)
    """)
    con.execute(f"""
        CREATE TABLE raw.part AS
        SELECT
            i AS p_partkey,
            'part ' || i AS p_name,
            'Manufacturer#' || ((i % 5) + 1) AS p_mfgr,
            'Brand#' || ((i % 5) + 1) || ((i % 5) + 1) AS p_brand,
            (['STANDARD','SMALL','MEDIUM','LARGE','ECONOMY','PROMO'])[(i % 6) + 1]
                || ' ' || (['ANODIZED','BURNISHED','PLATED','POLISHED','BRUSHED'])[(i % 5) + 1]
                || ' ' || (['TIN','NICKEL','BRASS','STEEL','COPPER'])[(i % 5) + 1] AS p_type,
            (i % 50) + 1 AS p_size,
            (['SM','LG','MED','JUMBO','WRAP'])[(i % 5) + 1] || ' BOX' AS p_container,
            (900 + (i % 1000) / 10.0)::DECIMAL(15,2) AS p_retailprice,
            '' AS p_comment
        FROM range(1, {n_part} + 1) r(i)
    """)
    con.execute(f"""
        CREATE TABLE raw.orders AS
        SELECT
            i AS o_orderkey,
            (floor(random() * {n_cust}) + 1)::BIGINT AS o_custkey,
            'F' AS o_orderstatus,
            0::DECIMAL(15,2) AS o_totalprice,
            (DATE '1992-01-01' + floor(random() * 2405)::INTEGER) AS o_orderdate,
            (['1-URGENT','2-HIGH','3-MEDIUM','4-NOT SPECIFIED','5-LOW'])[(i % 5) + 1] AS o_orderpriority,
            'Clerk#' || lpad(((i % 1000) + 1)::VARCHAR, 9, '0') AS o_clerk,
            0 AS o_shippriority,
            '' AS o_comment
        FROM range(1, {n_orders} + 1) r(i)
    """)
    con.execute(f"""
        CREATE TABLE raw.lineitem AS
        WITH lines AS (
            SELECT o.o_orderkey, o.o_orderdate, n.l AS l_linenumber
            FROM raw.orders o,
                 range(1, (o.o_orderkey % 7) + 2) n(l)
        )
        SELECT
            o_orderkey AS l_orderkey,
            (floor(random() * {n_part}) + 1)::BIGINT AS l_partkey,
            (floor(random() * {n_supp}) + 1)::BIGINT AS l_suppkey,
            l_linenumber,
            (floor(random() * 50) + 1)::DECIMAL(15,2) AS l_quantity,
            0::DECIMAL(15,2) AS l_extendedprice,
            round(random() * 0.10, 2)::DECIMAL(15,2) AS l_discount,
            round(random() * 0.08, 2)::DECIMAL(15,2) AS l_tax,
            'N' AS l_returnflag,
            'O' AS l_linestatus,
            o_orderdate + (floor(random() * 120) + 1)::INTEGER AS l_shipdate,
            o_orderdate + (floor(random() * 90) + 30)::INTEGER AS l_commitdate,
            o_orderdate + (floor(random() * 150) + 2)::INTEGER AS l_receiptdate,
            'DELIVER IN PERSON' AS l_shipinstruct,
            (['AIR','MAIL','SHIP','TRUCK','RAIL','FOB','REG AIR'])[(l_linenumber % 7) + 1] AS l_shipmode,
            '' AS l_comment
        FROM lines
    """)
    # Price = quantity x part retail price, as in TPC-H
    con.execute("""
        UPDATE raw.lineitem l SET l_extendedprice = l.l_quantity * p.p_retailprice
        FROM raw.part p WHERE l.l_partkey = p.p_partkey
    """)
    con.execute("""
        UPDATE raw.orders o SET o_totalprice = t.total
        FROM (
            SELECT l_orderkey, sum(l_extendedprice * (1 - l_discount) * (1 + l_tax))::DECIMAL(15,2) AS total
            FROM raw.lineitem GROUP BY l_orderkey
        ) t
        WHERE o.o_orderkey = t.l_orderkey
    """)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sf", type=float, default=0.1, help="TPC-H scale factor (default 0.1)")
    parser.add_argument("--synthetic", action="store_true", help="skip the tpch extension")
    args = parser.parse_args()

    for path in (DB_PATH, DB_PATH + ".wal"):
        if os.path.exists(path):
            os.remove(path)

    con = duckdb.connect(DB_PATH)
    con.execute("CREATE SCHEMA raw")

    source = "synthetic"
    if not args.synthetic:
        try:
            load_tpch(con, args.sf)
            source = "tpch extension"
        except duckdb.Error as exc:
            print(f"tpch extension unavailable ({str(exc).splitlines()[0]}); using synthetic generator")
    if source == "synthetic":
        load_synthetic(con, args.sf)

    # Business-effective timestamp for SCD2: every customer exists from the start of the order history
    con.execute("ALTER TABLE raw.customer ADD COLUMN updated_at TIMESTAMP DEFAULT TIMESTAMP '1992-01-01'")

    counts = con.execute("""
        SELECT (SELECT count(*) FROM raw.customer), (SELECT count(*) FROM raw.orders),
               (SELECT count(*) FROM raw.lineitem)
    """).fetchone()
    print(f"Loaded raw schema from {source} at sf={args.sf}: "
          f"{counts[0]:,} customers, {counts[1]:,} orders, {counts[2]:,} order lines")
    con.close()


if __name__ == "__main__":
    main()
