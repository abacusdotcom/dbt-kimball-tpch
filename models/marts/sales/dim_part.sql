-- SCD Type 1 part dimension: current attributes only
select
    {{ surrogate_key(['part_id']) }} as part_sk,
    part_id,
    part_name,
    manufacturer,
    brand,
    part_type,
    part_size,
    container,
    retail_price
from {{ ref('stg_tpch__part') }}
