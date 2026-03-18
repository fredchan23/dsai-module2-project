with eligible_deliveries as (
    select
        c.customer_state,
        o.order_id,
        o.is_late,
        o.delivery_days,
        o.days_to_ship,
        o.revenue_incl_freight
    from {{ ref('fct_orders') }} as o
    left join {{ ref('dim_customers') }} as c
        on o.customer_unique_id = c.customer_unique_id
    where o.order_status = 'delivered'
        and o.order_delivered_customer_ts is not null
        and o.order_estimated_delivery_ts is not null
)
select
    customer_state,
    count(*) as eligible_delivery_order_count,
    sum(case when not is_late then 1 else 0 end) as on_time_delivery_order_count,
    sum(case when is_late then 1 else 0 end) as late_delivery_order_count,
    coalesce(
        sum(case when not is_late then 1 else 0 end)::float / nullif(count(*), 0),
        0
    ) as on_time_delivery_rate,
    avg(delivery_days) as average_delivery_days,
    avg(days_to_ship) as average_days_to_ship,
    sum(revenue_incl_freight) as revenue_incl_freight
from eligible_deliveries
group by 1