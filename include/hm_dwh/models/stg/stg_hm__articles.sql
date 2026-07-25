select
    article_id,
    cast(product_code as integer) as product_code,
    prod_name as product_name,
    product_type_name,
    product_group_name,
    graphical_appearance_name,
    colour_group_name,
    perceived_colour_value_name,
    perceived_colour_master_name,
    department_name,
    index_name,
    index_group_name,
    section_name,
    garment_group_name,
    detail_desc as detail_description
from {{ ref('raw_articles') }}
