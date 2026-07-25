select
    t_dat,
    customer_id,
    article_id,
    price,
    sales_channel_id,
    ingestion_ts
from {{ source('raw', 'transactions') }}
