
  
    

create or replace transient table OLIST.DEV.mart_customer_rfm_raw
    
    
    
    as (with snapshot_date as (
    select max(order_date) as as_of_date
    from OLIST.DEV.fct_orders
),
customer_orders as (
    select
        o.customer_unique_id,
        min(c.customer_state) as customer_state,
        min(o.order_date) as first_order_date,
        max(o.order_date) as last_order_date,
        count(*) as frequency_orders,
        sum(o.revenue_incl_freight) as monetary_value
    from OLIST.DEV.fct_orders as o
    left join OLIST.DEV.dim_customers as c
        on o.customer_unique_id = c.customer_unique_id
    group by 1
)
select
    c.customer_unique_id,
    c.customer_state,
    c.first_order_date,
    c.last_order_date,
    datediff('day', c.last_order_date, s.as_of_date) as recency_days,
    c.frequency_orders,
    c.monetary_value,
    coalesce(c.monetary_value / nullif(c.frequency_orders, 0), 0) as average_order_value,
    s.as_of_date as rfm_snapshot_date
from customer_orders as c
cross join snapshot_date as s
    )
;


  