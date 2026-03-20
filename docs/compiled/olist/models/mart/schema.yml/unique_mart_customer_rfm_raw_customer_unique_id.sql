
    
    

select
    customer_unique_id as unique_field,
    count(*) as n_records

from OLIST.DEV.mart_customer_rfm_raw
where customer_unique_id is not null
group by customer_unique_id
having count(*) > 1


