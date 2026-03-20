# Olist dbt Project

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Conda Env](https://img.shields.io/badge/Conda-spark-44A833.svg)](https://docs.conda.io/)
[![dbt-snowflake](https://img.shields.io/badge/dbt--snowflake-1.11.3-orange.svg)](https://hub.getdbt.com/dbt-labs/dbt_snowflake/latest/)
[![Dagster](https://img.shields.io/badge/Dagster-1.12.19-2F7DF6.svg)](https://dagster.io/)
[![Warehouse](https://img.shields.io/badge/Warehouse-Snowflake-56B9EB.svg)](https://www.snowflake.com/)

End-to-end dbt project for the [Olist Brazilian e-commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), using **Snowflake** with raw sources in `OLIST.RAW` and dbt-built models materialized in `OLIST.DEV`. Raw data was ingested from BigQuery via GCS Parquet export and loaded into Snowflake using `COPY INTO`. This project transforms that raw layer into analytics-ready models.

## At a Glance

- Data flow: **BigQuery -> GCS (Parquet) -> Snowflake RAW -> dbt DEV marts**
- Warehouse: **Snowflake** (`OLIST.RAW` for sources, `OLIST.DEV` for transformed models)
- Transformation: **dbt** (`src` -> `dim`/`fct` -> `mart`)
- Orchestration: **Dagster** (`my_dbt_dagster_project`)

## Table of Contents

- [Dataset Overview](#dataset-overview)
- [Prerequisites](#prerequisites)
- [Snowflake Bootstrap (Run Once)](#snowflake-bootstrap-run-once)
- [Project Setup](#project-setup)
- [Raw Data Ingestion (BQ -> GCS -> Snowflake)](#raw-data-ingestion-bq---gcs---snowflake)
- [dbt Commands](#dbt-commands)
- [Project Structure](#project-structure)
- [Orchestration with Dagster](#orchestration-with-dagster)
- [Troubleshooting](#troubleshooting)

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

## Snowflake Bootstrap (Run Once)

Use the worksheet script in `snowflakes-setup.md` to initialize Snowflake objects for this project:

1. Creates `OLIST` database with `RAW` and `DEV` schemas.
2. Creates roles/users (`TRANSFORM`, `REPORTER`, `dbt`, `PRESET`) and grants permissions.
3. Loads all 9 raw OLIST tables into `OLIST.RAW` from GCS Parquet folders via `INFER_SCHEMA` + `COPY INTO`.

Run both SQL blocks in this order:

1. `Snowflake data import (manual)`
2. `Snowflake user and role creation`

File: `snowflakes-setup.md`

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

To create and use the dbt model layer in `OLIST.DEV`, run the companion grants in `grant_dev_schema.sql` as an account admin.

---

## Project Setup

### 1. Create and activate the shared conda environment

```bash
cd /path/to/dsai-module2-project
conda env create -f environment.spark.yml
conda activate spark
```

If you already have the environment, update it with:

```bash
cd /path/to/dsai-module2-project
conda env update -f environment.spark.yml --prune
```

This repository uses the existing `spark` conda environment for hands-on work. Learners can use the checked-in `environment.spark.yml` file instead of creating a separate virtual environment.

### 2. Install the local Dagster package

From the workspace root:

```bash
conda activate spark
cd /path/to/dsai-module2-project
pip install -e "my_dbt_dagster_project[dev]"
```

### 3. Configure dbt profile from template

This repo ships a safe template at `olist/profiles.template.yml`.

Create your local profile from it:

```bash
cd /path/to/dsai-module2-project/olist
cp profiles.template.yml profiles.yml
```

Then edit `profiles.yml` with your own Snowflake account/user/key details. The profile name must match `dbt_project.yml` (`olist`).

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
      schema: DEV
      warehouse: COMPUTE_WH
      threads: 1
```

> **Security note:** Never commit `profiles.yml` with real credentials. Use environment variables or a secrets manager for shared/CI environments:
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

> **Why this path was used:** This began as a team project, and the original raw exports were first landed in a teammate-owned GCS location for collaborative ingestion work. To make the workflow reproducible and independent for my own setup, I then moved the data into my own GCS path. From there, I extended the work as a personal learning exercise and side project by loading the same raw data into Snowflake and using dbt to build the transformation layer documented in this repository.

1. **BigQuery export** — tables exported as Parquet (Snappy compressed) to GCS bucket `gs://olist-snowflake-export/olist_export/`
2. **Snowflake GCS stage** — external stage `olist_gcs_stage` using storage integration `gcs_olist_integration`
3. **COPY INTO** — schema inferred via `INFER_SCHEMA`, data loaded with `MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE`

The same ingestion pattern is codified in `snowflakes-setup.md` for repeatable setup.

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

Run these from `olist/`:

```bash
cd /path/to/dsai-module2-project/olist

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

### Publish docs to root `docs/` (GitHub Pages compatible)

`dbt docs generate` writes files to `olist/target/`. GitHub Pages expects real files in a tracked folder, so this repo syncs those artifacts to root `docs/`.

Run from repo root:

```bash
conda run -n spark ./scripts/sync_docs_from_target.sh
```

Typical flow:

```bash
cd /path/to/dsai-module2-project/olist
dbt docs generate

cd /path/to/dsai-module2-project
conda run -n spark ./scripts/sync_docs_from_target.sh
```

---

## Project Structure

```
olist/
├── dbt_project.yml          # Project config — seed column types, schema defaults
├── profiles.template.yml    # Commit-safe template for learner setup
├── profiles.yml             # Local Snowflake profile (git-ignored, do not commit)
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

## Orchestration with Dagster

dbt models are orchestrated by Dagster via the `my_dbt_dagster_project` package at the workspace root (sibling to `olist/`).

### Quick Start

```bash
cd /path/to/dsai-module2-project
conda activate spark
pip install -e "my_dbt_dagster_project[dev]"
cd my_dbt_dagster_project
dagster dev
```

Open **http://localhost:3000/** to access the Dagster UI.

### Package Structure

| File | Purpose |
|---|---|
| `assets.py` | `olist_dbt_assets` — runs `dbt build` (run + test) for all models |
| `project.py` | `DbtProject` resolving `../olist` as the dbt project root |
| `definitions.py` | Wires assets, schedules, and `DbtCliResource` |
| `schedules.py` | Daily schedule (midnight UTC) materialising all models via `fqn:*` |

### Install (once)

```bash
pip install -e "my_dbt_dagster_project[dev]"
```

For full setup details and troubleshooting, see [dagster-setup.md](dagster-setup.md).

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
