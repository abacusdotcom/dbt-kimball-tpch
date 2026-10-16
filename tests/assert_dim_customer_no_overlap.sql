-- SCD2 integrity: no customer may have two versions whose validity windows overlap.
-- Overlaps would make the point-in-time join in fct_order_lines fan out.
select
    a.customer_id,
    a.valid_from as version_a_from,
    a.valid_to   as version_a_to,
    b.valid_from as version_b_from,
    b.valid_to   as version_b_to
from {{ ref('dim_customer') }} a
join {{ ref('dim_customer') }} b
    on  a.customer_id = b.customer_id
    and a.customer_sk <> b.customer_sk
    and a.valid_from < b.valid_to
    and b.valid_from < a.valid_to
