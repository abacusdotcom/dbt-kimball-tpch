-- Current state of each customer. History comes from snapshots/snp_customer.yml, not from here.
select
    c_custkey     as customer_id,
    c_name        as customer_name,
    c_nationkey   as nation_id,
    c_mktsegment  as market_segment,
    c_acctbal     as account_balance,
    updated_at
from {{ source('tpch', 'customer') }}
