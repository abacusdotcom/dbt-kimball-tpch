-- Nation with its region folded in: a small, fixed hierarchy used by customer and supplier
select
    n.n_nationkey  as nation_id,
    n.n_name       as nation_name,
    r.r_regionkey  as region_id,
    r.r_name       as region_name
from {{ source('tpch', 'nation') }} n
join {{ source('tpch', 'region') }} r
    on n.n_regionkey = r.r_regionkey
