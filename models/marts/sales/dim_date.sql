{#
    Calendar dimension covering the TPC-H order history (1992-1998).
    Smart integer key YYYYMMDD, as Kimball recommends for date dimensions:
    readable, sortable and derivable in the fact without a lookup.
#}
with days as (
    select cast(d as date) as date_day
    from generate_series(date '1992-01-01', date '1998-12-31', interval 1 day) t(d)
)

select
    cast(strftime(date_day, '%Y%m%d') as integer) as date_key,
    date_day,
    extract(year from date_day)                   as calendar_year,
    extract(quarter from date_day)                as calendar_quarter,
    extract(month from date_day)                  as month_number,
    strftime(date_day, '%B')                      as month_name,
    strftime(date_day, '%Y-%m')                   as year_month,
    extract(isodow from date_day)                 as day_of_week,
    strftime(date_day, '%A')                      as day_name,
    extract(isodow from date_day) in (6, 7)       as is_weekend
from days
