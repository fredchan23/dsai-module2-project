
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select order_purchase_timestamp
from OLIST.RAW.olist_orders_dataset
where order_purchase_timestamp is null



  
  
      
    ) dbt_internal_test