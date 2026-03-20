
    
    



with __dbt__cte__src_sellers as (
select
    cast("seller_id" as varchar(32)) as seller_id,
    cast("seller_zip_code_prefix" as varchar(5)) as seller_zip_code_prefix,
    trim("seller_city") as seller_city,
    trim("seller_state") as seller_state
from OLIST.RAW.raw_sellers
) select seller_id
from __dbt__cte__src_sellers
where seller_id is null


