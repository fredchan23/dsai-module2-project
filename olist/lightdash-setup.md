# Lightdash Setup for the Olist dbt Project

This guide documents a practical path to replace the current Preset embedded dashboard with a Lightdash dashboard backed by the `olist` dbt project.

## Recommended approach

| Option | Best for | Recommendation |
|---|---|---|
| Lightdash Cloud | Fastest evaluation with minimal ops | **Recommended first step** |
| Self-hosted Lightdash | Full control over infra and auth | Use after KPI parity is confirmed |

For this repo, the cleanest rollout is to start with **Lightdash Cloud**, validate the KPI outputs against the current Preset dashboard, then retire the Preset embed once the Lightdash dashboard is published.

## Why Lightdash fits this project

- The semantic layer can stay in the dbt project instead of being redefined in the BI tool.
- Your Snowflake marts are already business-ready and organized for dashboarding.
- Metrics and labels now live beside the dbt models in `models/mart/schema.yml`.
- dbt `exposures` can track the published Lightdash dashboard in project lineage.

## Lightdash-ready marts in this repo

Start with these models when building the replacement dashboard:

- `mart_monthly_sales` → revenue trend, orders, customers, AOV
- `mart_top_products` → product/category revenue and unit volume
- `mart_seller_performance` → seller leaderboard and service quality
- `mart_delivery_performance` → on-time delivery by geography
- `mart_customer_rfm_scored` → customer segment mix

## Option A — Lightdash Cloud

### 1. Create a Lightdash project

- Sign up or log in at `https://app.lightdash.cloud`
- Create a new project

### 2. Connect Snowflake

Use the same warehouse target as your dbt project:

- **Warehouse type:** `Snowflake`
- **Account:** `vrsugdf-gx74482` (or your org-account identifier from Snowsight)
- **Database:** `OLIST`
- **Schema:** `DEV`
- **Warehouse:** `COMPUTE_WH`
- **Role:** preferably `REPORTER`
- **User:** use a read-only reporting user

> For the **Account** field, enter only the Snowflake account identifier/subdomain — for example `vrsugdf-gx74482`. Do **not** paste `https://...snowflakecomputing.com`, and do **not** include extra path segments.

> You can reuse the existing `PRESET` / `REPORTER` access pattern or create a dedicated `LIGHTDASH` user with the same read-only grants.

### 3. Connect the dbt project

In the dbt project connection section:

- **Git provider:** `GitHub`
- **Repository:** your repo containing this project
- **Branch:** your main working branch
- **Project directory path:** `/olist`

### 4. Refresh the project

After saving the connections:

- trigger a Lightdash project refresh
- confirm these explores are available:
  - `Monthly Sales`
  - `Top Products`
  - `Seller Performance`
  - `Delivery Performance`
  - `Customer RFM Segments`

### 5. Rebuild the executive dashboard

Suggested first chart set:

1. Monthly revenue trend from `Monthly Sales`
2. Top product categories by revenue from `Top Products`
3. Seller revenue leaderboard from `Seller Performance`
4. On-time delivery rate by state from `Delivery Performance`
5. Customer segment split from `Customer RFM Segments`

## Option B — Self-hosted evaluation

If you want to test Lightdash on your own infrastructure:

1. follow the official self-host instructions from the Lightdash docs
2. point the instance to the same Snowflake warehouse and Git-backed dbt project
3. publish the dashboard only after KPI validation is complete

Official references:

- `https://github.com/lightdash/lightdash`
- `https://docs.lightdash.com/`

## Migration checklist

- [ ] Keep the current Preset dashboard live during migration
- [ ] Recreate the KPI views in Lightdash
- [ ] Compare revenue, orders, and top-product outputs against Preset
- [ ] Publish the final Lightdash dashboard URL
- [ ] Replace the placeholder Lightdash URL in `models/dashboards.yml`
- [ ] Retire the old Cloud Run Preset embed

## Final note

A placeholder exposure named `lightdash_executive_dashboard` has been added in `models/dashboards.yml`. Once the dashboard is live, update its `url` to the published Lightdash dashboard link.
