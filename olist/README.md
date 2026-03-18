# Olist dbt Project

End-to-end dbt project for the [Olist Brazilian e-commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), targeting **Snowflake** (`OLIST.RAW`). Raw data was ingested from BigQuery via GCS Parquet export and loaded into Snowflake using `COPY INTO`. This project transforms that raw layer into analytics-ready models.

---

## Dataset Overview

Nine raw tables covering the full order lifecycle:

| Table | Description |
|---|---|
| `raw_orders` | Order lifecycle with purchase, approval, and delivery timestamps |
| `raw_order_items` | Line items per order — product, seller, price, freight |
| `raw_order_payments` | Payment method and value per order (supports split payments) |
| `raw_order_reviews` | Customer review scores and comments |
| `raw_customers` | Customer dimension with `customer_id` (per-order surrogate) and `customer_unique_id` (natural key for repeat buyers) |
| `raw_products` | Product catalog with category and physical dimensions |
| `raw_sellers` | Seller master — city, state |
| `raw_geolocation` | Zip prefix → latitude/longitude reference |
| `raw_category_translation` | Portuguese → English product category map |

> **Note on customers:** Each order gets a unique `customer_id`. Use `customer_unique_id` to identify repeat buyers across orders.

See `dataset-info.md` for the full schema diagram.

---

## Prerequisites

| Requirement | Version / Notes |
|---|---|
| Python | 3.8+ |
| conda environment | `spark` |
| dbt-snowflake | 1.11.x (`pip install dbt-snowflake`) |
| Snowflake account | Role `TRANSFORM`, warehouse `COMPUTE_WH` |
| Private key pair | RSA key pair (PKCS8 PEM, passphrase-protected) |

### Snowflake Role Privileges Required

Run once as an account admin before using dbt:

```sql
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE TRANSFORM;
GRANT USAGE ON DATABASE OLIST TO ROLE TRANSFORM;
GRANT USAGE ON SCHEMA OLIST.RAW TO ROLE TRANSFORM;
GRANT CREATE TABLE ON SCHEMA OLIST.RAW TO ROLE TRANSFORM;
GRANT SELECT ON ALL TABLES IN SCHEMA OLIST.RAW TO ROLE TRANSFORM;
GRANT SELECT ON FUTURE TABLES IN SCHEMA OLIST.RAW TO ROLE TRANSFORM;
```

---

## Project Setup

### 1. Activate environment

```bash
conda activate spark
cd /path/to/dsai-module2-project/olist
```

### 2. Install dbt Snowflake adapter

```bash
pip install dbt-snowflake==1.11.3
```

### 3. Configure `profiles.yml`

The profile file lives **inside the project directory** (`olist/profiles.yml`), not `~/.dbt/`. Profile name must match `dbt_project.yml` (`olist`).

```yaml
olist:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: <account-locator>        # e.g. vrsugdf-gx74482
      user: <snowflake-user>
      role: TRANSFORM
      private_key: |
        -----BEGIN ENCRYPTED PRIVATE KEY-----
        <base64-encoded-key>
        -----END ENCRYPTED PRIVATE KEY-----
      private_key_passphrase: <passphrase>
      database: OLIST
      schema: RAW
      warehouse: COMPUTE_WH
      threads: 1
```

> **Security note:** Do not commit `profiles.yml` with real credentials to version control. Use environment variables or a secrets manager for shared/CI environments:
> ```yaml
> private_key_passphrase: "{{ env_var('DBT_PRIVATE_KEY_PASSPHRASE') }}"
> ```

### 4. Generate RSA key pair (if not already done)

```bash
# Generate encrypted private key
openssl genrsa 2048 | openssl pkcs8 -topk8 -v2 aes256 -out rsa_key.p8

# Extract public key
openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub
```

Then assign the public key to the Snowflake user:
```sql
ALTER USER dbt SET RSA_PUBLIC_KEY='<contents of rsa_key.pub without header/footer>';
```

### 5. Validate connection

```bash
dbt debug
```

All checks must pass before running any dbt commands.

---

## Raw Data Ingestion (BQ → GCS → Snowflake)

Raw tables were loaded into `OLIST.RAW` via:

1. **BigQuery export** — tables exported as Parquet (Snappy compressed) to GCS bucket `gs://olist-snowflake-export/olist_export/`
2. **Snowflake GCS stage** — external stage `olist_gcs_stage` using storage integration `gcs_olist_integration`
3. **COPY INTO** — schema inferred via `INFER_SCHEMA`, data loaded with `MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE`

To re-ingest a table:
```sql
-- Re-infer schema and reload (example: raw_orders)
CREATE OR REPLACE TABLE OLIST.RAW.raw_orders USING TEMPLATE (
  SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
  FROM TABLE(INFER_SCHEMA(
    LOCATION => '@olist_gcs_stage/raw_orders/',
    FILE_FORMAT => 'PARQUET'
  ))
);

COPY INTO OLIST.RAW.raw_orders
  FROM @olist_gcs_stage/raw_orders/
  FILE_FORMAT = (TYPE = PARQUET)
  MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;
```

---

## dbt Commands

```bash
# Validate connection and config
dbt debug

# Run all models
dbt run

# Run source freshness checks
dbt source freshness

# Test all sources and models
dbt test

# Test sources only
dbt test --select source:olist_raw

# Compile without executing
dbt compile

# View DAG lineage (generates target/manifest.json)
dbt ls
```

---

## Project Structure

```
olist/
├── dbt_project.yml          # Project config — seed column types, schema defaults
├── profiles.yml             # Snowflake connection profile (not committed with secrets)
├── models/
│   ├── sources.yml          # Source definitions pointing to OLIST.RAW raw_* tables
│   └── example/             # Starter example models (not production)
├── seeds/
│   ├── schema.yml           # Seed metadata and data tests (CSV-based seeds)
│   └── *.csv                # Raw CSV seed files (alternative local ingestion path)
├── macros/                  # Custom Jinja macros
├── tests/                   # Singular data tests
├── snapshots/               # SCD Type 2 snapshots
└── target/                  # Compiled artifacts (git-ignored)
```

---

## Troubleshooting

| Error | Likely Cause | Fix |
|---|---|---|
| `002043: Object does not exist` | Database/schema missing or role lacks USAGE | Run privilege grants above as account admin |
| `003001: Insufficient privileges` | Role cannot CREATE DATABASE | Admin must create database and grant USAGE |
| `JWT token is invalid` | Private key format or passphrase wrong | Regenerate key pair; verify PEM encoding is PKCS8 |
| `schema RAW_RAW created` | `+schema: RAW` set in both `profiles.yml` and `dbt_project.yml` seeds block | Remove `+schema` from seeds block in `dbt_project.yml` |
| Column type mismatch on seed load | dbt inferred wrong type from CSV | Add explicit `+column_types` in `dbt_project.yml` seeds config |
| Case sensitivity errors | Snowflake folds unquoted identifiers to uppercase | Keep `+quote_columns: false` in seeds config (current default) |
| `dbt seed` loads to wrong schema | Profile schema and seeds `+schema` override interact | Confirm `profiles.yml` schema matches intended target |
