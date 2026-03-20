
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select units_sold
from OLIST.DEV.mart_top_products
where units_sold is null



  
  
      
    ) dbt_internal_test