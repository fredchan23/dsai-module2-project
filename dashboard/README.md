# Olist BI Dashboard

A story-driven Streamlit dashboard over the Olist dbt mart tables in Snowflake.

## Sections

| Section | Source mart |
|---|---|
| Business Overview | `mart_monthly_sales` |
| Sales & Growth | `mart_monthly_sales`, `mart_top_products` |
| Customer Health | `mart_customer_rfm_scored` |
| Seller & Delivery | `mart_seller_performance`, `mart_delivery_performance` |

## Local setup

### 1. Install dependencies

```bash
pip install -r dashboard/requirements.txt
```

### 2. Configure Snowflake credentials

```bash
cp dashboard/.env.example dashboard/.env
```

Edit `dashboard/.env`. Choose **one** auth method:

**Option A — Inline private key (recommended)**
```
SNOWFLAKE_ACCOUNT=vrsugdf-gx74482
SNOWFLAKE_USER=dbt
SNOWFLAKE_ROLE=TRANSFORM
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=OLIST
SNOWFLAKE_SCHEMA=DEV
SNOWFLAKE_PRIVATE_KEY_BODY=-----BEGIN ENCRYPTED PRIVATE KEY-----\n...\n-----END ENCRYPTED PRIVATE KEY-----\n
SNOWFLAKE_PRIVATE_KEY_PASSPHRASE=your_passphrase
```

Paste the full PEM body on one line with `\n` replacing each newline (same format as `olist/profiles.yml` → `private_key`).

**Option B — Private key file**
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

**Option C — Password**
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

Opens at http://localhost:8501.

## Deploy to Streamlit Community Cloud

1. **Push this repo to GitHub** (public repo, or private on a paid Streamlit plan).

2. **Go to [share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub.

3. **Click "New app"** and fill in:
   - Repository: `fredchan23/dsai-module2-project` (or your fork)
   - Branch: `main`
   - Main file path: `dashboard/app.py`

4. **Add secrets** — click "Advanced settings" → "Secrets" and paste the contents of `dashboard/.streamlit/secrets.toml.example` with your real values filled in:

   ```toml
   SNOWFLAKE_ACCOUNT = "vrsugdf-gx74482"
   SNOWFLAKE_USER = "dbt"
   SNOWFLAKE_ROLE = "TRANSFORM"
   SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
   SNOWFLAKE_DATABASE = "OLIST"
   SNOWFLAKE_SCHEMA = "DEV"
   SNOWFLAKE_PRIVATE_KEY_BODY = "-----BEGIN ENCRYPTED PRIVATE KEY-----\n...\n-----END ENCRYPTED PRIVATE KEY-----\n"
   SNOWFLAKE_PRIVATE_KEY_PASSPHRASE = "your_passphrase"
   ```

5. **Click "Deploy"**. Streamlit Cloud installs `dashboard/requirements.txt` automatically and launches the app.

> **Note:** `dashboard/.env` is gitignored and never committed. Secrets are injected at runtime via Streamlit Cloud's secrets manager.

## Running tests

```bash
python -m pytest dashboard/tests/ -v
```

Unit tests run without Snowflake credentials. The live integration test (`test_live_load_monthly_sales`) is skipped unless `SNOWFLAKE_ACCOUNT` is set in the environment.
