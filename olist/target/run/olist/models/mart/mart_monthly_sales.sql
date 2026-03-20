
  
    

create or replace transient table OLIST.DEV.mart_monthly_sales
    
    
    
    as (with monthly_orders as (
    select
        cast(date_trunc('month', order_date) as date) as month_start_date,
        count(*) as order_count,
        count(distinct customer_unique_id) as customer_count,
        sum(gmv) as gross_merchandise_value,
        sum(revenue_incl_freight) as revenue_incl_freight,
        sum(case when is_delivered then 1 else 0 end) as delivered_order_count
    from OLIST.DEV.fct_orders
    group by 1
),
calendar_months as (
    select distinct
        cast(date_trunc('month', date_day) as date) as month_start_date,
        year_num,
        month_num,
        month_name,
        quarter_num
    from OLIST.DEV.dim_date
)
select
    m.month_start_date,
    c.year_num,
    c.quarter_num,
    c.month_num,
    c.month_name,
    m.order_count,
    m.customer_count,
    m.delivered_order_count,
    m.gross_merchandise_value,
    m.revenue_incl_freight,
    coalesce(m.revenue_incl_freight / nullif(m.order_count, 0), 0) as average_order_value
from monthly_orders as m
inner join calendar_months as c
    on m.month_start_date = c.month_start_date
    )
;


  