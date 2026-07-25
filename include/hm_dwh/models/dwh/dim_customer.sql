select
    {{ dbt_utils.generate_surrogate_key(['c.customer_id']) }} as customer_sk,
    c.customer_id,
    c.has_fashion_news,
    c.is_active,
    c.club_member_status,
    c.fashion_news_frequency,
    c.age,
    b.band_name as age_band,
    c.postal_code
from {{ ref('stg_hm__customers') }} as c
left join {{ ref('seed_age_bands') }} as b
    on c.age between b.min_age and b.max_age
