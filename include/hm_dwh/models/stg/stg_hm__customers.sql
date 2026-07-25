select
    customer_id,
    coalesce(fn, 0)::boolean as has_fashion_news,
    coalesce(active, 0)::boolean as is_active,
    club_member_status,
    -- fold the stray 'None' string into 'NONE'; true nulls stay null
    case
        when upper(fashion_news_frequency) = 'NONE' then 'NONE'
        else fashion_news_frequency
    end as fashion_news_frequency,
    age::smallint as age,
    postal_code
from {{ ref('raw_customers') }}
