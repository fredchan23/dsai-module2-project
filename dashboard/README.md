# Olist BI Dashboard

A story-driven Streamlit dashboard over the Olist dbt mart tables in Snowflake.

## Sections

| Section | Source mart |
|---|---|
| Business Overview | `mart_monthly_sales` |
| Sales & Growth | `mart_monthly_sales`, `mart_top_products` |
| Customer Health | `mart_customer_rfm_scored` |
| Seller & Delivery | `mart_seller_performance`, `mart_delivery_performance` |

## Setup

### 1. Install dependencies

```bash
pip install -r dashboard/requirements.txt
```

### 2. Configure Snowflake credentials

```bash
cp dashboard/.env.example dashboard/.env
```

Edit `dashboard/.env`. Choose **one** auth method:

**Option A — Private key (recommended)**
```
SNOWFLAKE_ACCOUNT=vrsugdf-gx74482
SNOWFLAKE_USER=dbt
SNOWFLAKE_ROLE=TRANSFORM
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=OLIST
SNOWFLAKE_SCHEMA=DEV
SNOWFLAKE_PRIVATE_KEY_PATH=/path/to/rsa_key.p8
SNOWFLAKE_PRIVATE_KEY_PASSPHRASE=your_passphrase
```

The project's RSA key is at `.secrets/lightdash/lightdash_rsa_key.p8` (passphrase: see `olist/profiles.yml`).

**Option B — Password**
```
SNOWFLAKE_ACCOUNT=vrsugdf-gx74482
SNOWFLAKE_USER=dbt
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ROLE=TRANSFORM
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=OLIST
SNOWFLAKE_SCHEMA=DEV
```

### 3. Run the dashboard

```bash
streamlit run dashboard/app.py
```

Opens at [http://localhost:8501](http://localhost:8501).

## Running tests

```bash
python -m pytest dashboard/tests/ -v
```

Unit tests run without Snowflake credentials. The live integration test (`test_live_load_monthly_sales`) is skipped unless `SNOWFLAKE_ACCOUNT` is set in the environment.
