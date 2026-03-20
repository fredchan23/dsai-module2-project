
    
    

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
) select
    product_id as unique_field,
    count(*) as n_records

from __dbt__cte__src_products
where product_id is not null
group by product_id
having count(*) > 1


