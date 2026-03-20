
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select order_purchase_ts
from OLIST.DEV.src_orders
where order_purchase_ts is null



  
  
      
    ) dbt_internal_test