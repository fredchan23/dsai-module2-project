
    
    



with __dbt__cte__src_category_translation as (
select
    trim("product_category_name") as product_category_name,
    trim("product_category_name_english") as product_category_name_english
from OLIST.RAW.raw_category_translation
) select product_category_name
from __dbt__cte__src_category_translation
where product_category_name is null


