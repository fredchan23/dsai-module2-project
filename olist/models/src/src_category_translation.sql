select
    trim("product_category_name") as product_category_name,
    trim("product_category_name_english") as product_category_name_english
from {{ source('olist_raw', 'raw_category_translation') }}
