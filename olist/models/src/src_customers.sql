select
    cast("customer_id" as varchar(32)) as customer_id,
    cast("customer_unique_id" as varchar(32)) as customer_unique_id,
    cast("customer_zip_code_prefix" as varchar(5)) as customer_zip_code_prefix,
    trim("customer_city") as customer_city,
    trim("customer_state") as customer_state
from {{ source('olist_raw', 'raw_customers') }}
