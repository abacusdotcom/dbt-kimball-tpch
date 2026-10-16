-- Proof of SCD2: customers with more than one version, and the revenue each version earned.
-- Compile with `dbt compile --profiles-dir .` and run the SQL in target/compiled/.
with versions as (
    select
        customer_id,
        customer_sk,
        market_segment,
        nation_name,
        valid_from,
        valid_to,
        is_current,
        count(*) over (partition by customer_id) as version_count
    from {{ ref('dim_customer') }}
)

select
    v.customer_id,
    v.market_segment,
    v.nation_name,
    cast(v.valid_from as date) as valid_from,
    cast(v.valid_to as date)   as valid_to,
    v.is_current,
    count(f.order_line_sk)     as order_lines,
    round(sum(f.net_amount), 2) as net_revenue
from versions v
left join {{ ref('fct_order_lines') }} f
    on f.customer_sk = v.customer_sk
where v.version_count > 1
group by all
order by 1, 4
limit 12
