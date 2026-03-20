
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select payment_sequential
from OLIST.RAW.olist_order_payments_dataset
where payment_sequential is null



  
  
      
    ) dbt_internal_test