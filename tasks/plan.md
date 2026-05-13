# Plan: Olist Streamlit BI Dashboard

## Problem Statement
Build a story-driven, multi-section Streamlit BI dashboard that makes the Olist dbt mart data legible to business stakeholders. Data lives in Snowflake (`OLIST.DEV.*`). Four sections: Overview, Sales & Growth, Customer RFM, Seller & Delivery.

---

## Architecture

```
dashboard/
├── app.py                  # entry point — page config, sidebar nav, section routing
├── db.py                   # Snowflake connection + @st.cache_data query functions
├── sections/
│   ├── overview.py         # KPI cards + monthly trend sparkline
│   ├── sales.py            # GMV trend, QoQ growth, top categories bar chart
│   ├── customers.py        # RFM scatter, segment donut, state filter
│   └── sellers.py          # seller table (sortable), delivery rate by state bar chart
├── requirements.txt
└── .env.example
```

### Snowflake Connection Details (from `olist/profiles.yml`)
- Account: `vrsugdf-gx74482`
- Database: `OLIST`, Schema: `DEV`
- Role: `TRANSFORM`, Warehouse: `COMPUTE_WH`
- Auth: encrypted private key (`dbt` user) — app will read key path + passphrase from env vars

### Mart Tables Queried
| Section | Table | Key Columns |
|---|---|---|
| Overview | `mart_monthly_sales` | `month_start_date`, `revenue_incl_freight`, `order_count`, `customer_count` |
| Sales | `mart_monthly_sales`, `mart_top_products` | `gross_merchandise_value`, `product_category_name_english`, `revenue_rank` |
| Customers | `mart_customer_rfm_scored` | `recency_days`, `frequency_orders`, `monetary_value`, `segment_label`, `customer_state` |
| Sellers | `mart_seller_performance`, `mart_delivery_performance` | `seller_id`, `revenue_incl_freight`, `on_time_delivery_rate`, `average_review_score` |

---

## Dependency Graph

```
Task 1: Scaffold (requirements, .env.example, app.py shell)
    └── Task 2: Snowflake connection layer (db.py)
            ├── Task 3: Overview section
            ├── Task 4: Sales & Growth section
            ├── Task 5: Customer RFM section
            └── Task 6: Seller & Delivery section
                    └── Task 7: Integration polish (layout, sidebar, final wiring)
```

Tasks 3–6 are independent of each other and can be built in any order after Task 2.

---

## Tasks

### Task 1 — Project Scaffold
**Goal:** Create the `dashboard/` directory with all boilerplate in place so the app can be launched (even if empty).

**Deliverables:**
- `dashboard/requirements.txt` — pins: `streamlit`, `snowflake-connector-python`, `pandas`, `plotly`, `python-dotenv`
- `dashboard/.env.example` — documents required env vars: `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_ROLE`, `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_DATABASE`, `SNOWFLAKE_SCHEMA`, `SNOWFLAKE_PRIVATE_KEY_PATH`, `SNOWFLAKE_PRIVATE_KEY_PASSPHRASE`
- `dashboard/app.py` — page config (`st.set_page_config`), sidebar with four section links, placeholder `st.write("Section: …")` for each

**Acceptance criteria:**
- `streamlit run dashboard/app.py` launches without error
- Sidebar shows four navigation options
- Selecting each option renders its placeholder text

**Verification:** Run `streamlit run dashboard/app.py`, confirm no import errors, sidebar visible.

---

### Task 2 — Snowflake Connection Layer
**Goal:** Implement `dashboard/db.py` — a single module that opens a Snowflake connection and exposes one cached query function per mart.

**Deliverables:**
- `get_connection()` — reads env vars, authenticates with private key (falls back to password if `SNOWFLAKE_PASSWORD` set), returns a `snowflake.connector` connection
- Five `@st.cache_data(ttl=3600)` functions:
  - `load_monthly_sales()` → DataFrame from `OLIST.DEV.MART_MONTHLY_SALES`
  - `load_top_products()` → DataFrame from `OLIST.DEV.MART_TOP_PRODUCTS`
  - `load_rfm_scored()` → DataFrame from `OLIST.DEV.MART_CUSTOMER_RFM_SCORED`
  - `load_seller_performance()` → DataFrame from `OLIST.DEV.MART_SELLER_PERFORMANCE`
  - `load_delivery_performance()` → DataFrame from `OLIST.DEV.MART_DELIVERY_PERFORMANCE`
- `dashboard/.env` (gitignored) — actual credentials for local dev

**Acceptance criteria:**
- Each `load_*()` function returns a non-empty DataFrame when called with valid credentials
- Cache hit on second call (verify via Streamlit's `st.cache_data` log or timing)
- `.env` is listed in `.gitignore` — credentials never committed

**Verification:** `python -c "from dashboard.db import load_monthly_sales; print(load_monthly_sales().shape)"` prints a non-zero shape.

---

### Task 3 — Overview Section
**Goal:** Implement `dashboard/sections/overview.py` — the first section a stakeholder sees.

**Deliverables:**
- Four KPI metric cards in a row: **Total Revenue**, **Total Orders**, **Unique Customers**, **Avg Order Value** (all-time from `mart_monthly_sales`)
- Line chart: monthly `revenue_incl_freight` over time (Plotly, formatted as BRL currency)
- Section header: "Business Overview"

**Acceptance criteria:**
- KPI numbers match a manual `SELECT SUM(revenue_incl_freight)` run against Snowflake
- Chart x-axis is `month_start_date` sorted ascending, no missing months
- Section renders in < 3s on first load (cold cache)

**Verification:** Load section, cross-check one KPI against a Snowflake query.

---

### Task 4 — Sales & Growth Section
**Goal:** Implement `dashboard/sections/sales.py` — revenue trends and product mix.

**Deliverables:**
- Grouped bar or area chart: monthly GMV (`gross_merchandise_value`) vs. revenue (`revenue_incl_freight`) side-by-side
- QoQ growth table: quarter, revenue, % change vs. prior quarter (computed from `mart_monthly_sales`)
- Horizontal bar chart: top 10 product categories by revenue (aggregated from `mart_top_products` grouped by `product_category_name_english`)
- Section header: "Sales & Growth"

**Acceptance criteria:**
- Top 10 categories sum ≤ total revenue (no double-counting)
- QoQ growth handles the first quarter gracefully (shows `—` not NaN)
- Chart tooltips show formatted BRL values

**Verification:** Confirm top category name and revenue value against a direct Snowflake query on `mart_top_products`.

---

### Task 5 — Customer RFM Section
**Goal:** Implement `dashboard/sections/customers.py` — customer segmentation view.

**Deliverables:**
- State filter (`st.selectbox`) — "All States" default, filters all charts below
- Scatter plot: x=`recency_days`, y=`frequency_orders`, bubble size=`monetary_value`, color=`segment_label` (6 distinct colors for the 6 RFM segments: champions, loyal_customers, recent_customers, at_risk, hibernating, potential_loyalists)
- Donut chart: count of customers per `segment_label`
- Summary table: segment, count, avg monetary value, avg recency days
- Section header: "Customer Health"

**Acceptance criteria:**
- Scatter plot renders with all 6 segment colors labeled correctly
- State filter correctly subsets all three visuals
- "All States" shows all customers; picking "SP" shows only SP customers
- Segment names displayed in title-case (not snake_case) in charts and table

**Verification:** Filter to a single state, count rows in summary table, cross-check against `SELECT COUNT(*) FROM MART_CUSTOMER_RFM_SCORED WHERE CUSTOMER_STATE = '<state>'`.

---

### Task 6 — Seller & Delivery Section
**Goal:** Implement `dashboard/sections/sellers.py` — seller performance and logistics health.

**Deliverables:**
- Sortable data table (`st.dataframe`): top 50 sellers by revenue — columns: seller_id (truncated), state, order count, revenue, on-time delivery rate (%), avg review score
- Horizontal bar chart: on-time delivery rate by `customer_state` (from `mart_delivery_performance`), sorted descending, color-coded (green ≥ 90%, amber 70-90%, red < 70%)
- KPI row: overall on-time delivery rate, avg review score, % sellers with review score ≥ 4
- Section header: "Seller & Delivery"

**Acceptance criteria:**
- Table default sort is revenue descending
- Delivery bar chart shows all states present in `mart_delivery_performance`
- Color thresholds (green/amber/red) applied correctly — visually verifiable

**Verification:** Identify the worst-performing state in the chart, cross-check its `on_time_delivery_rate` value against Snowflake.

---

### Task 7 — Integration & Polish
**Goal:** Wire all sections into `app.py`, apply consistent styling, and validate the full app end-to-end.

**Deliverables:**
- `app.py` updated: imports all four section modules, routes sidebar selection to correct `render()` call
- Consistent Plotly theme across all charts (single color palette, matching font)
- Sidebar: shows app title "Olist BI Dashboard", section nav, and a "Data as of: {max month}" timestamp pulled from `mart_monthly_sales`
- `dashboard/README.md` — setup instructions: clone, create `.env`, `pip install -r requirements.txt`, `streamlit run app.py`

**Acceptance criteria:**
- All four sections render without error in a single session
- Navigating between sections does not re-query Snowflake (cache hit confirmed)
- "Data as of" timestamp matches `MAX(month_start_date)` from `mart_monthly_sales`
- No hardcoded credentials anywhere in source files

**Verification:** Full walkthrough of all four sections; check `st.cache_data` is not bypassed on nav.

---

## Checkpoints

| After | Gate |
|---|---|
| Task 1 | App launches, sidebar visible — proceed to Task 2 |
| Task 2 | All `load_*()` return real data — proceed to Tasks 3–6 |
| Tasks 3–6 | Each section renders correctly in isolation — proceed to Task 7 |
| Task 7 | Full end-to-end walkthrough passes — dashboard is shippable |

---

## Not Doing
- **Auth/login wall** — no user authentication; this is an internal stakeholder tool
- **Write-back or annotations** — read-only dashboard
- **Brazil state choropleth map** — requires GeoJSON + folium/plotly geo setup; bar chart by state achieves the same insight with far less complexity
- **Automated refresh** — `st.cache_data` TTL is sufficient; no background refresh thread
- **Mobile layout** — Streamlit's default responsive layout is acceptable for now
- **dbt run trigger from UI** — out of scope; Dagster handles orchestration

---

## Open Questions
- Should the Snowflake schema be `DEV` or a dedicated `PROD` schema? (Assuming `DEV` for now — change `SNOWFLAKE_SCHEMA` env var when prod schema exists.)
- Private key auth vs. username/password for the Streamlit app: private key is more secure but requires distributing the `.p8` file. Consider using a service account with username/password for the dashboard if the key is hard to distribute.
