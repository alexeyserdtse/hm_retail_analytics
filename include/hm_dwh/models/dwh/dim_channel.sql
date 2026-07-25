select
    {{ dbt_utils.generate_surrogate_key(['sales_channel_id']) }} as channel_sk,
    sales_channel_id,
    channel_name
from {{ ref('seed_sales_channels') }}
