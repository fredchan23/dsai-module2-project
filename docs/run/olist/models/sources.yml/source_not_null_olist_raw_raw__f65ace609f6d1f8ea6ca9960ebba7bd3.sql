
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select "product_category_name"
from OLIST.RAW.raw_category_translation
where "product_category_name" is null



  
  
      
    ) dbt_internal_test