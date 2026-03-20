
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select monetary_score
from OLIST.RAW.mart_customer_rfm_scored
where monetary_score is null



  
  
      
    ) dbt_internal_test