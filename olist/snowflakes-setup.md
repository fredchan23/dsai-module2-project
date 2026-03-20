## Snowflake data import (manual)

Resources:
* [Snowflake Key-Pair Authentication](https://docs.snowflake.com/en/user-guide/key-pair-auth)
* [Snowflake INFER_SCHEMA](https://docs.snowflake.com/en/sql-reference/functions/infer_schema)

Copy these SQL statements into a Snowflake Worksheet, adjust placeholders, then run them.

Assumptions for this script:
* You load OLIST raw data from GCS Parquet folders (one folder per raw table).
* Your external stage is named `olist_gcs_stage` and points to the base path containing raw table folders.
* The folders are named exactly as the raw tables (for example `raw_orders/`, `raw_products/`).

```sql {#snowflake_import}
-- Set up defaults
CREATE WAREHOUSE IF NOT EXISTS COMPUTE_WH;
USE WAREHOUSE COMPUTE_WH;

-- Recreate database for a clean bootstrap
DROP DATABASE IF EXISTS OLIST CASCADE;
CREATE DATABASE OLIST;

CREATE SCHEMA IF NOT EXISTS OLIST.RAW;
CREATE SCHEMA IF NOT EXISTS OLIST.DEV;

USE DATABASE OLIST;
USE SCHEMA RAW;

-- Optional: create stage here if not already created.
-- Replace the URL and integration with your environment values.
-- CREATE OR REPLACE STAGE olist_gcs_stage
--   URL = 'gcs://<your-bucket>/<your-prefix>/'
--   STORAGE_INTEGRATION = gcs_olist_integration
--   FILE_FORMAT = (TYPE = PARQUET);

-- Build tables from Parquet schema and load data.
-- Repeat the same pattern for all raw OLIST datasets.

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

CREATE OR REPLACE TABLE OLIST.RAW.raw_order_items USING TEMPLATE (
  SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
  FROM TABLE(INFER_SCHEMA(
    LOCATION => '@olist_gcs_stage/raw_order_items/',
    FILE_FORMAT => 'PARQUET'
  ))
);

COPY INTO OLIST.RAW.raw_order_items
  FROM @olist_gcs_stage/raw_order_items/
  FILE_FORMAT = (TYPE = PARQUET)
  MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

CREATE OR REPLACE TABLE OLIST.RAW.raw_order_payments USING TEMPLATE (
  SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
  FROM TABLE(INFER_SCHEMA(
    LOCATION => '@olist_gcs_stage/raw_order_payments/',
    FILE_FORMAT => 'PARQUET'
  ))
);

COPY INTO OLIST.RAW.raw_order_payments
  FROM @olist_gcs_stage/raw_order_payments/
  FILE_FORMAT = (TYPE = PARQUET)
  MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

CREATE OR REPLACE TABLE OLIST.RAW.raw_order_reviews USING TEMPLATE (
  SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
  FROM TABLE(INFER_SCHEMA(
    LOCATION => '@olist_gcs_stage/raw_order_reviews/',
    FILE_FORMAT => 'PARQUET'
  ))
);

COPY INTO OLIST.RAW.raw_order_reviews
  FROM @olist_gcs_stage/raw_order_reviews/
  FILE_FORMAT = (TYPE = PARQUET)
  MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

CREATE OR REPLACE TABLE OLIST.RAW.raw_customers USING TEMPLATE (
  SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
  FROM TABLE(INFER_SCHEMA(
    LOCATION => '@olist_gcs_stage/raw_customers/',
    FILE_FORMAT => 'PARQUET'
  ))
);

COPY INTO OLIST.RAW.raw_customers
  FROM @olist_gcs_stage/raw_customers/
  FILE_FORMAT = (TYPE = PARQUET)
  MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

CREATE OR REPLACE TABLE OLIST.RAW.raw_products USING TEMPLATE (
  SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
  FROM TABLE(INFER_SCHEMA(
    LOCATION => '@olist_gcs_stage/raw_products/',
    FILE_FORMAT => 'PARQUET'
  ))
);

COPY INTO OLIST.RAW.raw_products
  FROM @olist_gcs_stage/raw_products/
  FILE_FORMAT = (TYPE = PARQUET)
  MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

CREATE OR REPLACE TABLE OLIST.RAW.raw_sellers USING TEMPLATE (
  SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
  FROM TABLE(INFER_SCHEMA(
    LOCATION => '@olist_gcs_stage/raw_sellers/',
    FILE_FORMAT => 'PARQUET'
  ))
);

COPY INTO OLIST.RAW.raw_sellers
  FROM @olist_gcs_stage/raw_sellers/
  FILE_FORMAT = (TYPE = PARQUET)
  MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

CREATE OR REPLACE TABLE OLIST.RAW.raw_geolocation USING TEMPLATE (
  SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
  FROM TABLE(INFER_SCHEMA(
    LOCATION => '@olist_gcs_stage/raw_geolocation/',
    FILE_FORMAT => 'PARQUET'
  ))
);

COPY INTO OLIST.RAW.raw_geolocation
  FROM @olist_gcs_stage/raw_geolocation/
  FILE_FORMAT = (TYPE = PARQUET)
  MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

CREATE OR REPLACE TABLE OLIST.RAW.raw_category_translation USING TEMPLATE (
  SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
  FROM TABLE(INFER_SCHEMA(
    LOCATION => '@olist_gcs_stage/raw_category_translation/',
    FILE_FORMAT => 'PARQUET'
  ))
);

COPY INTO OLIST.RAW.raw_category_translation
  FROM @olist_gcs_stage/raw_category_translation/
  FILE_FORMAT = (TYPE = PARQUET)
  MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;
```

## Snowflake user and role creation

Copy these SQL statements into a Snowflake Worksheet, replace key placeholders, and run them.

```sql {#snowflake_setup}
-- Use an admin role
USE ROLE ACCOUNTADMIN;

-- Create the `transform` role
DROP ROLE IF EXISTS TRANSFORM;
CREATE ROLE TRANSFORM;
GRANT ROLE TRANSFORM TO ROLE ACCOUNTADMIN;

-- Create the default warehouse if necessary
GRANT OPERATE ON WAREHOUSE COMPUTE_WH TO ROLE TRANSFORM;

-- Create the `dbt` user and assign to role
DROP USER IF EXISTS dbt;
CREATE USER IF NOT EXISTS dbt
  LOGIN_NAME='dbt'
  TYPE=SERVICE
  RSA_PUBLIC_KEY="<<Add Your Public Key File's content here>>"
  DEFAULT_ROLE=TRANSFORM
  DEFAULT_WAREHOUSE='COMPUTE_WH'
  DEFAULT_NAMESPACE='OLIST.RAW'
  COMMENT='DBT user used for data transformation';

GRANT ROLE TRANSFORM to USER dbt;

-- Set up permissions to role `transform`
GRANT ALL ON WAREHOUSE COMPUTE_WH TO ROLE TRANSFORM;
GRANT ALL ON DATABASE OLIST to ROLE TRANSFORM;
GRANT ALL ON ALL SCHEMAS IN DATABASE OLIST to ROLE TRANSFORM;
GRANT ALL ON FUTURE SCHEMAS IN DATABASE OLIST to ROLE TRANSFORM;
GRANT ALL ON ALL TABLES IN SCHEMA OLIST.RAW to ROLE TRANSFORM;
GRANT ALL ON FUTURE TABLES IN SCHEMA OLIST.RAW to ROLE TRANSFORM;
GRANT ALL ON SCHEMA OLIST.DEV to ROLE TRANSFORM;
GRANT ALL ON ALL TABLES IN SCHEMA OLIST.DEV to ROLE TRANSFORM;
GRANT ALL ON FUTURE TABLES IN SCHEMA OLIST.DEV to ROLE TRANSFORM;

-- Create the user and permissions for Preset.io
USE ROLE ACCOUNTADMIN;

DROP ROLE IF EXISTS REPORTER;
CREATE ROLE REPORTER;

DROP USER IF EXISTS PRESET;
CREATE USER PRESET
  LOGIN_NAME='preset'
  TYPE=SERVICE
  RSA_PUBLIC_KEY="<<Add Your Public Key File's content here>>"
  DEFAULT_WAREHOUSE='COMPUTE_WH'
  DEFAULT_ROLE=REPORTER
  DEFAULT_NAMESPACE='OLIST.DEV'
 COMMENT='Preset user for creating reports';

GRANT ROLE REPORTER TO USER PRESET;
GRANT ROLE REPORTER TO ROLE ACCOUNTADMIN;
GRANT ALL ON WAREHOUSE COMPUTE_WH TO ROLE REPORTER;
GRANT USAGE ON DATABASE OLIST TO ROLE REPORTER;
GRANT USAGE ON ALL SCHEMAS IN DATABASE OLIST to ROLE REPORTER;
GRANT USAGE ON FUTURE SCHEMAS IN DATABASE OLIST to ROLE REPORTER;
GRANT SELECT ON ALL TABLES IN SCHEMA OLIST.DEV to ROLE REPORTER;
GRANT SELECT ON FUTURE TABLES IN SCHEMA OLIST.DEV to ROLE REPORTER;
