with order_items as (
    select order_id,
        order_item_id,
        product_id,
        seller_id,
        shipping_limit_ts,
        item_price,
        freight_value,
        item_price + freight_value as total_item_value
        from {{ ref('src_order_items') }}
),
products as (
    select product_id,
        product_category_name_english
    from {{ ref('dim_products') }}
),
sellers as (
    select seller_id,
        seller_state
    from {{ ref('dim_sellers') }}
),
orders as (
    select order_id,
        customer_unique_id,
        order_date,
        order_status,
        is_delivered,
        is_late,
        delivery_days
    from {{ ref('fct_orders') }}
)
select oi.order_id,
    oi.order_item_id,
    oi.product_id,
    oi.seller_id,
    o.customer_unique_id,
    o.order_date,
    o.order_status,
    o.is_delivered,
    o.is_late,
    o.delivery_days,
    oi.shipping_limit_ts,
    oi.item_price,
    oi.freight_value,
    oi.total_item_value,
    p.product_category_name_english,
    s.seller_state
from order_items as oi
    left join orders as o on oi.order_id = o.order_id
    left join products as p on oi.product_id = p.product_id
    left join sellers as s on oi.seller_id = s.seller_id