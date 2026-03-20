
  
    

create or replace transient table OLIST.DEV.fact_reviews
    
    
    
    as (with reviews_deduped as (
    select review_id,
        order_id,
        review_score,
        review_comment_title,
        review_comment_message,
        review_creation_ts,
        review_answer_ts
    from OLIST.DEV.src_order_reviews
    qualify row_number() over (
            partition by order_id
            order by review_creation_ts desc
        ) = 1
),
orders as (
    select order_id,
        customer_unique_id,
        order_date
    from OLIST.DEV.fct_orders
)
select r.review_id,
    r.order_id,
    o.customer_unique_id,
    o.order_date,
    r.review_score,
    case
        when r.review_score <= 2 then true
        else false
    end as is_low_score,
    r.review_comment_title,
    r.review_comment_message,
    r.review_creation_ts,
    r.review_answer_ts
from reviews_deduped as r
    left join orders as o on r.order_id = o.order_id
    )
;


  