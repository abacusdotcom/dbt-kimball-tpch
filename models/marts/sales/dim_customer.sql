{#
    SCD Type 2 customer dimension: one row per customer version.
    Built from the snapshot; tracked attributes are market segment and nation.
    valid_to is closed with a high date so the fact can use a half-open range
    (valid_from <= event < valid_to) without null handling.
#}
with snp as (
    select * from {{ ref('snp_customer') }}
),

nation as (
    select * from {{ ref('stg_tpch__nation') }}
)

select
    {{ surrogate_key(['snp.c_custkey', 'snp.dbt_valid_from']) }} as customer_sk,
    snp.c_custkey                                                 as customer_id,
    snp.c_name                                                    as customer_name,
    snp.c_mktsegment                                              as market_segment,
    nation.nation_name,
    nation.region_name,
    snp.dbt_valid_from                                            as valid_from,
    coalesce(snp.dbt_valid_to, cast('{{ var("scd_high_date") }}' as timestamp)) as valid_to,
    snp.dbt_valid_to is null                                      as is_current
from snp
left join nation
    on snp.c_nationkey = nation.nation_id
