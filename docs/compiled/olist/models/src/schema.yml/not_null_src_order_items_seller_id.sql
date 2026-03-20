
    
    



with __dbt__cte__src_order_items as (
select
    cast("order_id" as varchar(32)) as order_id,
    cast("order_item_id" as number(10, 0)) as order_item_id,
    cast("product_id" as varchar(32)) as product_id,
    cast("seller_id" as varchar(32)) as seller_id,
    cast("shipping_limit_date" as timestamp_ntz) as shipping_limit_ts,
    cast("price" as number(10, 2)) as item_price,
    cast("freight_value" as number(10, 2)) as freight_value
from OLIST.RAW.raw_order_items
) select seller_id
from __dbt__cte__src_order_items
where seller_id is null


