
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select representative_customer_id
from OLIST.DEV.dim_customers
where representative_customer_id is null



  
  
      
    ) dbt_internal_test