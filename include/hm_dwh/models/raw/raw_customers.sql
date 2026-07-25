select
    customer_id,
    -- quotes are load-bearing: they force the view to expose lowercase names
    "FN" as fn,  -- noqa: RF06
    "Active" as active,  -- noqa: RF06
    club_member_status,
    fashion_news_frequency,
    age,
    postal_code,
    ingestion_ts
from {{ source('raw', 'customers') }}
