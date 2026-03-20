
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select is_delivered
from OLIST.RAW.fct_orders
where is_delivered is null



  
  
      
    ) dbt_internal_test