with item_agg as (
    select
        order_id,
        count(*) as order_item_count,
        sum(item_price) as gmv,
        sum(item_price + freight_value) as revenue_incl_freight
    from {{ ref('src_order_items') }}
    group by order_id
),
payment_agg as (
    select
        order_id,
        sum(payment_value) as total_payment_value,
        count(*) as payment_count
    from {{ ref('src_order_payments') }}
    group by order_id
),
review_agg as (
    select
        order_id,
        avg(review_score) as avg_review_score
    from {{ ref('src_order_reviews') }}
    group by order_id
),
orders_enriched as (
    select
        o.order_id,
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
        1 as order_count
    from {{ ref('src_orders') }} as o
    left join {{ ref('src_customers') }} as c
        on o.customer_id = c.customer_id
    left join item_agg as i
        on o.order_id = i.order_id
    left join payment_agg as p
        on o.order_id = p.order_id
    left join review_agg as r
        on o.order_id = r.order_id
)

select
    order_id,
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
    order_count
from orders_enriched
