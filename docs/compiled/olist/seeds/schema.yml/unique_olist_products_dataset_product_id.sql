
    
    

select
    product_id as unique_field,
    count(*) as n_records

from OLIST.RAW.olist_products_dataset
where product_id is not null
group by product_id
having count(*) > 1


