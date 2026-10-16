{#
    Sales fact at the grain of one row per order line.

    The customer join is point-in-time: each line picks the customer version
    that was valid on the order date, so revenue is attributed to the segment
    and nation the customer had when they bought, not the one they have now.
#}
with lines as (
    select * from {{ ref('stg_tpch__lineitem') }}
),

orders as (
    select * from {{ ref('stg_tpch__orders') }}
)

select
    {{ surrogate_key(['lines.order_id', 'lines.line_number']) }} as order_line_sk,
    lines.order_id,
    lines.line_number,
    cust.customer_sk,
    {{ surrogate_key(['lines.part_id']) }}                       as part_sk,
    {{ surrogate_key(['lines.supplier_id']) }}                   as supplier_sk,
    cast(strftime(orders.order_date, '%Y%m%d') as integer)       as order_date_key,
    orders.order_priority,
    lines.ship_mode,
    lines.quantity,
    lines.extended_price,
    lines.discount,
    lines.tax,
    lines.extended_price * (1 - lines.discount)                  as net_amount,
    lines.extended_price * (1 - lines.discount) * (1 + lines.tax) as gross_amount
from lines
join orders
    on lines.order_id = orders.order_id
left join {{ ref('dim_customer') }} cust
    on  orders.customer_id = cust.customer_id
    and orders.order_date >= cust.valid_from
    and orders.order_date <  cust.valid_to
