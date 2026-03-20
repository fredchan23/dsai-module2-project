
    
    

select
    month_start_date as unique_field,
    count(*) as n_records

from OLIST.DEV.mart_monthly_sales
where month_start_date is not null
group by month_start_date
having count(*) > 1


