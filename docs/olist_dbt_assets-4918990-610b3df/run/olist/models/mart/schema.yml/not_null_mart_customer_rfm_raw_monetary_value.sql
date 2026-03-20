
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select monetary_value
from OLIST.DEV.mart_customer_rfm_raw
where monetary_value is null



  
  
      
    ) dbt_internal_test