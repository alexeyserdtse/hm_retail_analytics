{% macro date_attributes(date_col) %}
    extract(year from {{ date_col }})                        as year,
    extract(quarter from {{ date_col }})                     as quarter,
    extract(month from {{ date_col }})                       as month,
    strftime({{ date_col }}, '%B')                           as month_name,
    extract(isodow from {{ date_col }})                      as iso_weekday,
    strftime({{ date_col }}, '%A')                           as weekday_name,
    extract(isodow from {{ date_col }}) in (6, 7)            as is_weekend
{% endmacro %}
