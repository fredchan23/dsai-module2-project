
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select product_id
from OLIST.DEV.mart_top_products
where product_id is null



  
  
      
    ) dbt_internal_test