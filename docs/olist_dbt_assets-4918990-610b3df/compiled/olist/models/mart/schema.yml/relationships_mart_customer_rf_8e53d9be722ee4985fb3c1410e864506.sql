
    
    

with child as (
    select customer_unique_id as from_field
    from OLIST.DEV.mart_customer_rfm_scored
    where customer_unique_id is not null
),

parent as (
    select customer_unique_id as to_field
    from OLIST.DEV.mart_customer_rfm_raw
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


