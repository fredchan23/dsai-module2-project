with customer_base as (
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
    from OLIST.DEV.src_customers
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