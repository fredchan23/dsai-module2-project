with product_performance as (
    select
        product_id,
        min(product_category_name_english) as product_category_name_english,
        count(distinct order_id) as order_count,
        count(*) as units_sold,
        sum(item_price) as gross_merchandise_value,
        sum(total_item_value) as revenue_incl_freight
    from OLIST.DEV.fct_order_items
    group by 1
)
select
    product_id,
    product_category_name_english,
    order_count,
    units_sold,
    gross_merchandise_value,
    revenue_incl_freight,
    coalesce(revenue_incl_freight / nullif(units_sold, 0), 0) as average_unit_revenue,
    dense_rank() over (order by revenue_incl_freight desc, product_id) as revenue_rank,
    dense_rank() over (
        partition by product_category_name_english
        order by revenue_incl_freight desc, product_id
    ) as category_revenue_rank
from product_performance