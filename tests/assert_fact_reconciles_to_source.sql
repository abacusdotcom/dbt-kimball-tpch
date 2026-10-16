-- Reconciliation: the fact must hold every source order line and the same total
-- extended price. Catches rows dropped or duplicated by the dimension joins.
with src as (
    select count(*) as line_count, sum(l_extendedprice) as extended_price
    from {{ source('tpch', 'lineitem') }}
),

fct as (
    select count(*) as line_count, sum(extended_price) as extended_price
    from {{ ref('fct_order_lines') }}
)

select src.*, fct.line_count as fct_line_count, fct.extended_price as fct_extended_price
from src, fct
where src.line_count <> fct.line_count
   or src.extended_price <> fct.extended_price
