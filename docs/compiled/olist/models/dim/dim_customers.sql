with  __dbt__cte__src_customers as (
select
    cast("customer_id" as varchar(32)) as customer_id,
    cast("customer_unique_id" as varchar(32)) as customer_unique_id,
    cast("customer_zip_code_prefix" as varchar(5)) as customer_zip_code_prefix,
    trim("customer_city") as customer_city,
    trim("customer_state") as customer_state
from OLIST.RAW.raw_customers
), customer_base as (
    select
        customer_unique_id,
        customer_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state,
        row_number() over (
            partition by customer_unique_id
            order by customer_id desc
        ) as rn,
        count(distinct customer_id) over (
            partition by customer_unique_id
        ) as customer_id_count
    from __dbt__cte__src_customers
)

select
    customer_unique_id,
    customer_id as representative_customer_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state,
    customer_id_count
from customer_base
where rn = 1