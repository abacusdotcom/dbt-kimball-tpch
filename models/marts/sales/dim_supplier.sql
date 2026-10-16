-- SCD Type 1 supplier dimension with the nation/region hierarchy folded in
select
    {{ surrogate_key(['s.supplier_id']) }} as supplier_sk,
    s.supplier_id,
    s.supplier_name,
    n.nation_name,
    n.region_name
from {{ ref('stg_tpch__supplier') }} s
left join {{ ref('stg_tpch__nation') }} n
    on s.nation_id = n.nation_id
