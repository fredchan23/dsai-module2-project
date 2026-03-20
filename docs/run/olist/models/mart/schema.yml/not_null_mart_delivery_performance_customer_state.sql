
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select customer_state
from OLIST.RAW.mart_delivery_performance
where customer_state is null



  
  
      
    ) dbt_internal_test