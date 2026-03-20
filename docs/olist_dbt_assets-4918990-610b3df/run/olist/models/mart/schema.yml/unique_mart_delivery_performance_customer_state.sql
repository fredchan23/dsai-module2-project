
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    customer_state as unique_field,
    count(*) as n_records

from OLIST.DEV.mart_delivery_performance
where customer_state is not null
group by customer_state
having count(*) > 1



  
  
      
    ) dbt_internal_test