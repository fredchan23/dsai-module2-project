
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select recency_score
from OLIST.RAW.mart_customer_rfm_scored
where recency_score is null



  
  
      
    ) dbt_internal_test