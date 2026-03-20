
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        segment_label as value_field,
        count(*) as n_records

    from OLIST.RAW.mart_customer_rfm_scored
    group by segment_label

)

select *
from all_values
where value_field not in (
    'champions','loyal_customers','recent_customers','at_risk','hibernating','potential_loyalists'
)



  
  
      
    ) dbt_internal_test