{% snapshot snap_article_price %}

{{
    config(
      unique_key='article_id',
      strategy='check',
      check_cols=['median_price'],
    )
}}

-- Latest observed monthly median price per article. Reads the raw layer only:
-- anything downstream of this snapshot must never feed back into it.
    with monthly as (
        select
            article_id,
            date_trunc('month', t_dat) as price_month,
            median(price) as median_price
        from {{ ref('raw_transactions') }}
        group by 1, 2
    )

    select
        article_id,
        price_month,
        median_price
    from monthly
    qualify row_number() over (partition by article_id order by price_month desc) = 1

{% endsnapshot %}
