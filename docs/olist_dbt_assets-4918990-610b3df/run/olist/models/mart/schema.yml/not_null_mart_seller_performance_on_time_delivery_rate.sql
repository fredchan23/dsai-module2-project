
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select on_time_delivery_rate
from OLIST.DEV.mart_seller_performance
where on_time_delivery_rate is null



  
  
      
    ) dbt_internal_test