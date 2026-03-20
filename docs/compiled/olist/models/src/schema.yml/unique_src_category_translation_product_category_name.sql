
    
    

with __dbt__cte__src_category_translation as (
select
    trim("product_category_name") as product_category_name,
    trim("product_category_name_english") as product_category_name_english
from OLIST.RAW.raw_category_translation
) select
    product_category_name as unique_field,
    count(*) as n_records

from __dbt__cte__src_category_translation
where product_category_name is not null
group by product_category_name
having count(*) > 1


