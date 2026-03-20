
    
    

with child as (
    select customer_unique_id as from_field
    from OLIST.DEV.fct_orders
    where customer_unique_id is not null
),

parent as (
    select customer_unique_id as to_field
    from OLIST.DEV.dim_customers
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


