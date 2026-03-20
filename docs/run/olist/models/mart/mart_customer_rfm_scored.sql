
  
    

create or replace transient table OLIST.DEV.mart_customer_rfm_scored
    
    
    
    as (with scored as (
    select
        customer_unique_id,
        customer_state,
        first_order_date,
        last_order_date,
        recency_days,
        frequency_orders,
        monetary_value,
        average_order_value,
        rfm_snapshot_date,
        6 - ntile(5) over (order by recency_days asc, customer_unique_id) as recency_score,
        ntile(5) over (order by frequency_orders asc, customer_unique_id) as frequency_score,
        ntile(5) over (order by monetary_value asc, customer_unique_id) as monetary_score
    from OLIST.DEV.mart_customer_rfm_raw
)
select
    customer_unique_id,
    customer_state,
    first_order_date,
    last_order_date,
    recency_days,
    frequency_orders,
    monetary_value,
    average_order_value,
    rfm_snapshot_date,
    recency_score,
    frequency_score,
    monetary_score,
    concat(recency_score, frequency_score, monetary_score) as rfm_score_code,
    case
        when recency_score >= 4 and frequency_score >= 4 and monetary_score >= 4 then 'champions'
        when recency_score >= 3 and frequency_score >= 4 and monetary_score >= 3 then 'loyal_customers'
        when recency_score = 5 and frequency_score <= 2 then 'recent_customers'
        when recency_score <= 2 and frequency_score >= 4 and monetary_score >= 3 then 'at_risk'
        when recency_score <= 2 and frequency_score <= 2 then 'hibernating'
        else 'potential_loyalists'
    end as segment_label
from scored
    )
;


  