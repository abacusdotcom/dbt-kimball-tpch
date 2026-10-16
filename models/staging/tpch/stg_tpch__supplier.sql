select
    s_suppkey    as supplier_id,
    s_name       as supplier_name,
    s_nationkey  as nation_id,
    s_acctbal    as account_balance
from {{ source('tpch', 'supplier') }}
