with spine as (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2018-09-01' as date)",
        end_date="cast('2020-10-01' as date)"
    ) }}
)

select
    cast(date_day as date) as date_day,
    {{ date_attributes('date_day') }}
from spine
