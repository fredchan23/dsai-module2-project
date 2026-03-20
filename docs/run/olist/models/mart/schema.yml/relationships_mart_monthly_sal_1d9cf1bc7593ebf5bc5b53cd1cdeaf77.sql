
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with child as (
    select month_start_date as from_field
    from OLIST.RAW.mart_monthly_sales
    where month_start_date is not null
),

parent as (
    select date_day as to_field
    from OLIST.RAW.dim_date
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null



  
  
      
    ) dbt_internal_test