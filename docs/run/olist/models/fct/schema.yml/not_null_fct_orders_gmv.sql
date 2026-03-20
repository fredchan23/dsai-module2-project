
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select gmv
from OLIST.RAW.fct_orders
where gmv is null



  
  
      
    ) dbt_internal_test