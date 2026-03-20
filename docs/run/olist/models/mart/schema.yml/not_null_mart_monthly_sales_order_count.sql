
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select order_count
from OLIST.RAW.mart_monthly_sales
where order_count is null



  
  
      
    ) dbt_internal_test