
    
    



with __dbt__cte__src_order_payments as (
select
    cast("order_id" as varchar(32)) as order_id,
    cast("payment_sequential" as number(10, 0)) as payment_sequential,
    trim("payment_type") as payment_type,
    cast("payment_installments" as number(10, 0)) as payment_installments,
    cast("payment_value" as number(10, 2)) as payment_value
from OLIST.RAW.raw_order_payments
) select payment_value
from __dbt__cte__src_order_payments
where payment_value is null


