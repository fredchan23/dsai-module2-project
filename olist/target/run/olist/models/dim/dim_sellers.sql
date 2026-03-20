
  
    

create or replace transient table OLIST.DEV.dim_sellers
    
    
    
    as (select
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
from OLIST.DEV.src_sellers
    )
;


  