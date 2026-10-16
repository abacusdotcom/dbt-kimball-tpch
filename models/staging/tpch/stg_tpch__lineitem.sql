select
    l_orderkey       as order_id,
    l_linenumber     as line_number,
    l_partkey        as part_id,
    l_suppkey        as supplier_id,
    l_quantity       as quantity,
    l_extendedprice  as extended_price,
    l_discount       as discount,
    l_tax            as tax,
    l_returnflag     as return_flag,
    l_linestatus     as line_status,
    l_shipdate       as ship_date,
    l_shipmode       as ship_mode
from {{ source('tpch', 'lineitem') }}
