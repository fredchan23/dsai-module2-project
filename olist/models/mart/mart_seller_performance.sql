with seller_orders as (
    select
        oi.seller_id,
        min(ds.seller_state) as seller_state,
        oi.order_id,
        min(oi.order_date) as order_date,
        sum(oi.item_price) as gross_merchandise_value,
        sum(oi.total_item_value) as revenue_incl_freight,
        count(*) as items_sold
    from {{ ref('fct_order_items') }} as oi
    left join {{ ref('dim_sellers') }} as ds
        on oi.seller_id = ds.seller_id
    group by 1, 3
),
order_delivery as (
    select
        order_id,
        order_status,
        order_delivered_customer_ts,
        order_estimated_delivery_ts,
        is_late,
        delivery_days,
        days_to_ship
    from {{ ref('fct_orders') }}
),
seller_orders_enriched as (
    select
        so.seller_id,
        so.seller_state,
        so.order_id,
        so.order_date,
        so.gross_merchandise_value,
        so.revenue_incl_freight,
        so.items_sold,
        od.order_status,
        od.order_delivered_customer_ts,
        od.order_estimated_delivery_ts,
        od.is_late,
        od.delivery_days,
        od.days_to_ship,
        fr.review_score,
        fr.is_low_score
    from seller_orders as so
    left join order_delivery as od
        on so.order_id = od.order_id
    left join {{ ref('fact_reviews') }} as fr
        on so.order_id = fr.order_id
)
select
    seller_id,
    seller_state,
    min(order_date) as first_order_date,
    max(order_date) as last_order_date,
    count(*) as order_count,
    sum(items_sold) as items_sold,
    sum(gross_merchandise_value) as gross_merchandise_value,
    sum(revenue_incl_freight) as revenue_incl_freight,
    coalesce(sum(revenue_incl_freight) / nullif(count(*), 0), 0) as average_order_revenue,
    sum(
        case
            when order_status = 'delivered'
                and order_delivered_customer_ts is not null
                and order_estimated_delivery_ts is not null
            then 1
            else 0
        end
    ) as eligible_delivery_order_count,
    sum(
        case
            when order_status = 'delivered'
                and order_delivered_customer_ts is not null
                and order_estimated_delivery_ts is not null
                and not is_late
            then 1
            else 0
        end
    ) as on_time_delivery_order_count,
    coalesce(
        sum(
            case
                when order_status = 'delivered'
                    and order_delivered_customer_ts is not null
                    and order_estimated_delivery_ts is not null
                    and not is_late
                then 1
                else 0
            end
        )::float
        / nullif(
            sum(
                case
                    when order_status = 'delivered'
                        and order_delivered_customer_ts is not null
                        and order_estimated_delivery_ts is not null
                    then 1
                    else 0
                end
            ),
            0
        ),
        0
    ) as on_time_delivery_rate,
    avg(delivery_days) as average_delivery_days,
    avg(days_to_ship) as average_days_to_ship,
    avg(review_score) as average_review_score,
    coalesce(sum(case when is_low_score then 1 else 0 end)::float / nullif(count(review_score), 0), 0) as low_score_review_rate
from seller_orders_enriched
group by 1, 2