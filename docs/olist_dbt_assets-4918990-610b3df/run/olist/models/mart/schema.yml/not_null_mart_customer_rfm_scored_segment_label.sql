
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select segment_label
from OLIST.DEV.mart_customer_rfm_scored
where segment_label is null



  
  
      
    ) dbt_internal_test