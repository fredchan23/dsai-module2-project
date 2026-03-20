
  
    

create or replace transient table OLIST.DEV.dim_date
    
    
    
    as (with  __dbt__cte__src_orders as (
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
), order_dates as (
    select
        cast(min(cast(order_purchase_ts as date)) as date) as min_date,
        cast(max(cast(order_estimated_delivery_ts as date)) as date) as max_date
    from __dbt__cte__src_orders
),
sequence as (
    select seq4() as day_offset
    from table(generator(rowcount => 5000))
),
date_spine as (
    select
        dateadd(day, s.day_offset, o.min_date) as date_day
    from sequence as s
    cross join order_dates as o
    where dateadd(day, s.day_offset, o.min_date) <= o.max_date
)

select
    date_day,
    year(date_day) as year_num,
    month(date_day) as month_num,
    day(date_day) as day_num,
    quarter(date_day) as quarter_num,
    monthname(date_day) as month_name,
    dayname(date_day) as day_name,
    iff(dayofweekiso(date_day) in (6, 7), true, false) as is_weekend
from date_spine
    )
;


  