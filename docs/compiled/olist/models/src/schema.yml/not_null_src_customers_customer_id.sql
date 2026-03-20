
    
    



with __dbt__cte__src_customers as (
select
    cast("customer_id" as varchar(32)) as customer_id,
    cast("customer_unique_id" as varchar(32)) as customer_unique_id,
    cast("customer_zip_code_prefix" as varchar(5)) as customer_zip_code_prefix,
    trim("customer_city") as customer_city,
    trim("customer_state") as customer_state
from OLIST.RAW.raw_customers
) select customer_id
from __dbt__cte__src_customers
where customer_id is null


