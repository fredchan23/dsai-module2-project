
    
    

select
    customer_state as unique_field,
    count(*) as n_records

from OLIST.DEV.mart_delivery_performance
where customer_state is not null
group by customer_state
having count(*) > 1


