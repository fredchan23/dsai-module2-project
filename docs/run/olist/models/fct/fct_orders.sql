
  
    

create or replace transient table OLIST.DEV.fct_orders
    
    
    
    as (with  __dbt__cte__src_order_items as (
select
    cast("order_id" as varchar(32)) as order_id,
    cast("order_item_id" as number(10, 0)) as order_item_id,
    cast("product_id" as varchar(32)) as product_id,
    cast("seller_id" as varchar(32)) as seller_id,
    cast("shipping_limit_date" as timestamp_ntz) as shipping_limit_ts,
    cast("price" as number(10, 2)) as item_price,
    cast("freight_value" as number(10, 2)) as freight_value
from OLIST.RAW.raw_order_items
),  __dbt__cte__src_order_payments as (
select
    cast("order_id" as varchar(32)) as order_id,
    cast("payment_sequential" as number(10, 0)) as payment_sequential,
    trim("payment_type") as payment_type,
    cast("payment_installments" as number(10, 0)) as payment_installments,
    cast("payment_value" as number(10, 2)) as payment_value
from OLIST.RAW.raw_order_payments
),  __dbt__cte__src_order_reviews as (
select
    cast("review_id" as varchar(32)) as review_id,
    cast("order_id" as varchar(32)) as order_id,
    cast("review_score" as number(2, 0)) as review_score,
    nullif(trim("review_comment_title"), '') as review_comment_title,
    nullif(trim("review_comment_message"), '') as review_comment_message,
    cast("review_creation_date" as timestamp_ntz) as review_creation_ts,
    cast("review_answer_timestamp" as timestamp_ntz) as review_answer_ts
from OLIST.RAW.raw_order_reviews
),  __dbt__cte__src_orders as (
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
),  __dbt__cte__src_customers as (
select
    cast("customer_id" as varchar(32)) as customer_id,
    cast("customer_unique_id" as varchar(32)) as customer_unique_id,
    cast("customer_zip_code_prefix" as varchar(5)) as customer_zip_code_prefix,
    trim("customer_city") as customer_city,
    trim("customer_state") as customer_state
from OLIST.RAW.raw_customers
), item_agg as (
    select order_id,
        count(*) as order_item_count,
        sum(item_price) as gmv,
        sum(item_price + freight_value) as revenue_incl_freight
     from __dbt__cte__src_order_items
    group by order_id
),
payment_agg as (
    select order_id,
        sum(payment_value) as total_payment_value,
        count(*) as payment_count
     from __dbt__cte__src_order_payments
    group by order_id
),
review_agg as (
    select order_id,
        avg(review_score) as avg_review_score
     from __dbt__cte__src_order_reviews
    group by order_id
),
orders_enriched as (
    select o.order_id,
        o.customer_id,
        c.customer_unique_id,
        o.order_status,
        o.order_purchase_ts,
        o.order_approved_ts,
        o.order_delivered_carrier_ts,
        o.order_delivered_customer_ts,
        o.order_estimated_delivery_ts,
        coalesce(i.order_item_count, 0) as order_item_count,
        coalesce(i.gmv, 0) as gmv,
        coalesce(i.revenue_incl_freight, 0) as revenue_incl_freight,
        coalesce(p.total_payment_value, 0) as total_payment_value,
        coalesce(p.payment_count, 0) as payment_count,
        r.avg_review_score,
        case
            when o.order_status = 'delivered' then true
            else false
        end as is_delivered,
        case
            when o.order_delivered_customer_ts > o.order_estimated_delivery_ts then true
            else false
        end as is_late,
        datediff(
            'day',
            o.order_purchase_ts,
            o.order_delivered_customer_ts
        ) as delivery_days,
        datediff(
            'day',
            o.order_purchase_ts,
            o.order_delivered_carrier_ts
        ) as days_to_ship,
        1 as order_count
    from __dbt__cte__src_orders as o
        left join __dbt__cte__src_customers as c on o.customer_id = c.customer_id
        left join item_agg as i on o.order_id = i.order_id
        left join payment_agg as p on o.order_id = p.order_id
        left join review_agg as r on o.order_id = r.order_id
)
select order_id,
    customer_id,
    customer_unique_id,
    cast(order_purchase_ts as date) as order_date,
    order_status,
    order_purchase_ts,
    order_approved_ts,
    order_delivered_carrier_ts,
    order_delivered_customer_ts,
    order_estimated_delivery_ts,
    order_item_count,
    gmv,
    revenue_incl_freight,
    total_payment_value,
    payment_count,
    avg_review_score,
    is_delivered,
    is_late,
    delivery_days,
    days_to_ship,
    order_count
from orders_enriched
    )
;


  