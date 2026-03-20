with __dbt__cte__src_products as (
select
    cast("product_id" as varchar(32)) as product_id,
    trim("product_category_name") as product_category_name,
    cast("product_name_lenght" as number(10, 0)) as product_name_length,
    cast("product_description_lenght" as number(10, 0)) as product_description_length,
    cast("product_photos_qty" as number(10, 0)) as product_photos_qty,
    cast("product_weight_g" as number(10, 0)) as product_weight_g,
    cast("product_length_cm" as number(10, 0)) as product_length_cm,
    cast("product_height_cm" as number(10, 0)) as product_height_cm,
    cast("product_width_cm" as number(10, 0)) as product_width_cm
from OLIST.RAW.raw_products
),  __dbt__cte__src_category_translation as (
select
    trim("product_category_name") as product_category_name,
    trim("product_category_name_english") as product_category_name_english
from OLIST.RAW.raw_category_translation
) select
    p.product_id,
    p.product_category_name,
    coalesce(t.product_category_name_english, 'unknown') as product_category_name_english,
    p.product_name_length,
    p.product_description_length,
    p.product_photos_qty,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm
from __dbt__cte__src_products as p
left join __dbt__cte__src_category_translation as t
    on p.product_category_name = t.product_category_name