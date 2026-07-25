-- SCD2 price history made queryable: one row per article per price version,
-- with the current-row indicator derived from the snapshot's validity range.
select
    {{ dbt_utils.generate_surrogate_key(['article_id', 'dbt_valid_from']) }} as price_version_sk,
    article_id,
    median_price,
    price_month,
    dbt_valid_from as valid_from,
    dbt_valid_to as valid_to,
    dbt_valid_to is null as is_current
from {{ ref('snap_article_price') }}
