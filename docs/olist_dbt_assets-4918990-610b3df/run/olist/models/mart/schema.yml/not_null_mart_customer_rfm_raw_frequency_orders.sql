
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select frequency_orders
from OLIST.DEV.mart_customer_rfm_raw
where frequency_orders is null



  
  
      
    ) dbt_internal_test