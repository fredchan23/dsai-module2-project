select
    cast("review_id" as varchar(32)) as review_id,
    cast("order_id" as varchar(32)) as order_id,
    cast("review_score" as number(2, 0)) as review_score,
    nullif(trim("review_comment_title"), '') as review_comment_title,
    nullif(trim("review_comment_message"), '') as review_comment_message,
    cast("review_creation_date" as timestamp_ntz) as review_creation_ts,
    cast("review_answer_timestamp" as timestamp_ntz) as review_answer_ts
from {{ source('olist_raw', 'raw_order_reviews') }}
