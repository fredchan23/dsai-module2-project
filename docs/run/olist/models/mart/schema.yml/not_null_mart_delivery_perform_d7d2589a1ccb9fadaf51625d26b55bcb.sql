
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select eligible_delivery_order_count
from OLIST.RAW.mart_delivery_performance
where eligible_delivery_order_count is null



  
  
      
    ) dbt_internal_test