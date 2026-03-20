# Olist Analytics Transformation Overview

This project transforms raw Olist e-commerce data into a layered analytics model designed for BI, KPI tracking, and customer/seller performance analysis.

## Transformation Layers

1. Source (`src_*`)
	- Standardizes raw tables into consistent field names and data types.
	- Applies basic quality checks such as `not_null` and `unique` on business keys.

2. Dimensions (`dim_*`)
	- Builds reusable conformed entities:
	  - `dim_customers` at `customer_unique_id` grain.
	  - `dim_products` enriched with translated category labels.
	  - `dim_sellers` with seller location attributes.
	  - `dim_date` for consistent calendar reporting.

3. Facts (`fct_*`, `fact_reviews`)
	- Captures transactional measures at business grains:
	  - `fct_orders` at `order_id` grain with lifecycle, delivery, and revenue metrics.
	  - `fct_order_items` at `(order_id, order_item_id)` grain for item-level revenue and volume.
	  - `fact_reviews` at `order_id` grain for customer sentiment and low-score flags.

4. Marts (`mart_*`)
	- Curated datasets for specific analytics use cases:
	  - Monthly sales trends.
	  - Top product performance.
	  - Customer RFM segmentation.
	  - Delivery service-level analysis.
	  - Seller performance monitoring.

## Input Schema Diagram

The diagram below shows how raw inputs are standardized into `src_*` models before feeding dimensions, facts, and marts.

```text
RAW INPUT TABLES
  customers ---------------------------> src_customers -----> dim_customers ---+
  products ----------------------------> src_products  -----> dim_products  --+ |
  sellers -----------------------------> src_sellers   -----> dim_sellers   -+ | |
  geolocation -------------------------> src_geolocation ----------------------+ | |
  product_category_name_translation --> src_category_translation --------------+ | |
  orders ------------------------------> src_orders ----------------------------+ | |
  order_items -------------------------> src_order_items -----------------------+ | |
  order_payments ----------------------> src_order_payments --------------------+ | |
  order_reviews -----------------------> src_order_reviews ---------------------+ | |
																								 +------v-v-v-------+
																								 | FACT LAYER        |
																								 | fct_orders        |
																								 | fct_order_items   |
																								 | fact_reviews      |
																								 +---------+---------+
																											  |
																											  v
																								 +-------------------+
																								 | MART LAYER        |
																								 | mart_monthly_sales|
																								 | mart_top_products |
																								 | mart_customer_rfm*|
																								 | mart_delivery_*   |
																								 | mart_seller_*     |
																								 +-------------------+
```

## Key Business Logic Highlights

- Revenue logic combines item price and freight to produce `revenue_incl_freight`.
- Delivery KPIs classify fulfillment into delivered/late outcomes and compute shipping and delivery lead times.
- Review signals derive `is_low_score` for quality monitoring.
- RFM marts convert raw customer behavior metrics into standardized segment labels.

## Data Quality and Integrity

The project enforces model reliability through:

- Key constraints (`not_null`, `unique`) on primary identifiers.
- Referential integrity tests (`relationships`) between facts, dimensions, and marts.
- Domain checks (`accepted_values`) for controlled business labels such as RFM segments.

