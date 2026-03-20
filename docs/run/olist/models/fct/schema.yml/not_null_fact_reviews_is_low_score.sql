
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select is_low_score
from OLIST.RAW.fact_reviews
where is_low_score is null



  
  
      
    ) dbt_internal_test