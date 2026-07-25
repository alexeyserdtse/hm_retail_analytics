select
    cast(t_dat as date)               as sale_date,
    customer_id,
    article_id,
    cast(price as decimal(12, 8))     as price,
    cast(sales_channel_id as tinyint) as sales_channel_id,
    ingestion_ts
from {{ ref('raw_transactions') }}
