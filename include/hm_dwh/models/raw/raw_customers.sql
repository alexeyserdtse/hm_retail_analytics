select
    customer_id,
    "FN" as fn,
    "Active" as active,
    club_member_status,
    fashion_news_frequency,
    age,
    postal_code,
    ingestion_ts
from {{ source('raw', 'customers') }}
