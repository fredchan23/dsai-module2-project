
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select recency_days
from OLIST.DEV.mart_customer_rfm_raw
where recency_days is null



  
  
      
    ) dbt_internal_test