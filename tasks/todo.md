# Olist Streamlit Dashboard — Task List

## Phase 1: Foundation
- [ ] **Task 1** — Project scaffold (`dashboard/` dir, `requirements.txt`, `.env.example`, `app.py` shell with sidebar nav)
- [ ] **Task 2** — Snowflake connection layer (`db.py`: `get_connection()` + 5 `@st.cache_data` `load_*()` functions)

## Phase 2: Sections (parallelizable after Task 2)
- [ ] **Task 3** — Overview section: KPI cards (revenue, orders, customers, AOV) + monthly revenue line chart
- [ ] **Task 4** — Sales & Growth section: GMV vs revenue chart, QoQ growth table, top 10 categories bar chart
- [ ] **Task 5** — Customer RFM section: state filter, RFM scatter plot, segment donut chart, summary table
- [ ] **Task 6** — Seller & Delivery section: seller performance table, on-time rate by state bar chart, KPI row

## Phase 3: Integration
- [ ] **Task 7** — Wire all sections into `app.py`, unified Plotly theme, "Data as of" timestamp, `dashboard/README.md`

## Checkpoints
- [ ] **CP1** (after Task 1): `streamlit run dashboard/app.py` launches, sidebar visible
- [ ] **CP2** (after Task 2): all `load_*()` return real Snowflake data, `.env` gitignored
- [ ] **CP3** (after Tasks 3–6): each section renders correctly in isolation
- [ ] **CP4** (after Task 7): full end-to-end walkthrough passes, no hardcoded credentials
