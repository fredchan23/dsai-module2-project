
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select revenue_incl_freight
from OLIST.DEV.fct_orders
where revenue_incl_freight is null



  
  
      
    ) dbt_internal_test