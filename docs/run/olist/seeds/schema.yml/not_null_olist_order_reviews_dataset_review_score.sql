
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select review_score
from OLIST.RAW.olist_order_reviews_dataset
where review_score is null



  
  
      
    ) dbt_internal_test