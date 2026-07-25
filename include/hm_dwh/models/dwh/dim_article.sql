with current_price as (
    select
        article_id,
        median_price as current_price
    from {{ ref('snap_article_price') }}
    where dbt_valid_to is null
)

select
    {{ dbt_utils.generate_surrogate_key(['a.article_id']) }} as article_sk,
    a.article_id,
    a.product_code,
    a.product_name,
    a.product_type_name,
    a.product_group_name,
    a.graphical_appearance_name,
    a.colour_group_name,
    a.perceived_colour_value_name,
    a.perceived_colour_master_name,
    a.department_name,
    a.index_name,
    a.index_group_name,
    a.section_name,
    a.garment_group_name,
    p.current_price
from {{ ref('stg_hm__articles') }} as a
left join current_price as p on a.article_id = p.article_id
