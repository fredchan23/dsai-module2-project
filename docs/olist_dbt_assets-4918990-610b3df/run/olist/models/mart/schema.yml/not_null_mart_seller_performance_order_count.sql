
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select order_count
from OLIST.DEV.mart_seller_performance
where order_count is null



  
  
      
    ) dbt_internal_test