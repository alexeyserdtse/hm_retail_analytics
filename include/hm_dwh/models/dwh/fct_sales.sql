{{
    config(
      materialized='incremental',
      incremental_strategy='delete+insert',
      unique_key='sale_month'
    )
}}

select
    {{ dbt_utils.generate_surrogate_key(['t.customer_id']) }} as customer_sk,
    {{ dbt_utils.generate_surrogate_key(['t.article_id']) }} as article_sk,
    {{ dbt_utils.generate_surrogate_key(['t.sales_channel_id']) }} as channel_sk,
    t.sale_date,
    date_trunc('month', t.sale_date) as sale_month,
    t.customer_id,
    t.article_id,
    count(*) as quantity,
    sum(t.price) as sales_amount
from {{ ref('stg_hm__transactions') }} as t
{% if var('month', none) %}
where date_trunc('month', t.sale_date) = cast('{{ var("month") }}-01' as date)
{% endif %}
group by all
