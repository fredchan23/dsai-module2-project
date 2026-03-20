
    
    

select
    order_id as unique_field,
    count(*) as n_records

from OLIST.RAW.olist_orders_dataset
where order_id is not null
group by order_id
having count(*) > 1


