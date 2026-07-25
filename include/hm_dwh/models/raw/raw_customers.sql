select
    customer_id,
    fn,
    active,
    club_member_status,
    fashion_news_frequency,
    age,
    postal_code,
    ingestion_ts
from {{ source('raw', 'customers') }}
