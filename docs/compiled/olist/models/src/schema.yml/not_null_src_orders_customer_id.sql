
    
    



with __dbt__cte__src_orders as (
select
    cast("order_id" as varchar(32)) as order_id,
    cast("customer_id" as varchar(32)) as customer_id,
    trim("order_status") as order_status,
    cast("order_purchase_timestamp" as timestamp_ntz) as order_purchase_ts,
    cast("order_approved_at" as timestamp_ntz) as order_approved_ts,
    cast("order_delivered_carrier_date" as timestamp_ntz) as order_delivered_carrier_ts,
    cast("order_delivered_customer_date" as timestamp_ntz) as order_delivered_customer_ts,
    cast("order_estimated_delivery_date" as timestamp_ntz) as order_estimated_delivery_ts
from OLIST.RAW.raw_orders
) select customer_id
from __dbt__cte__src_orders
where customer_id is null


