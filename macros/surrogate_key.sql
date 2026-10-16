{#
    Deterministic hash surrogate key from one or more columns.

    Same idea as dbt_utils.generate_surrogate_key, kept local so the project
    has no package dependencies. Nulls are replaced with a sentinel so that
    (1, null) and (null, 1) never collide.

    Why a hash and not an IDENTITY column: in ELT the dimension is rebuilt on
    every run, so an incrementing integer would change between runs and break
    any downstream table that stored it. A hash of the business key (plus the
    version start for SCD2 rows) is stable across rebuilds and can be computed
    independently in the fact without a lookup.
#}
{% macro surrogate_key(columns) -%}
    md5(
        {%- for col in columns %}
        coalesce(cast({{ col }} as varchar), '_null_')
        {%- if not loop.last %} || '|' || {% endif %}
        {%- endfor %}
    )
{%- endmacro %}
