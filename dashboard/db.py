"""Snowflake connection and cached query functions for the Olist BI dashboard."""
import os

import pandas as pd
import snowflake.connector
import streamlit as st
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    load_pem_private_key,
)
from dotenv import load_dotenv

load_dotenv()

# Bridge st.secrets → os.environ for Streamlit Community Cloud deployment
try:
    for _k, _v in st.secrets.items():
        if _k not in os.environ:
            os.environ[_k] = str(_v)
except Exception:
    pass

_DB = os.getenv("SNOWFLAKE_DATABASE", "OLIST")
_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA", "DEV")


def get_connection():
    account = os.environ["SNOWFLAKE_ACCOUNT"]
    user = os.environ["SNOWFLAKE_USER"]
    role = os.getenv("SNOWFLAKE_ROLE", "TRANSFORM")
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
    database = _DB
    schema = _SCHEMA

    password = os.getenv("SNOWFLAKE_PASSWORD")
    key_path = os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH")
    key_body = os.getenv("SNOWFLAKE_PRIVATE_KEY_BODY")  # inline PEM string

    if key_path or key_body:
        passphrase = os.getenv("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE", "").encode() or None
        if key_body:
            pem = key_body.replace("\\n", "\n").encode()
        else:
            with open(key_path, "rb") as f:
                pem = f.read()
        private_key = load_pem_private_key(pem, password=passphrase, backend=default_backend())
        private_key_bytes = private_key.private_bytes(
            encoding=Encoding.DER,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption(),
        )
        return snowflake.connector.connect(
            account=account, user=user, role=role, warehouse=warehouse,
            database=database, schema=schema, private_key=private_key_bytes,
            ocsp_fail_open=True, insecure_mode=True,
        )

    return snowflake.connector.connect(
        account=account, user=user, password=password, role=role,
        warehouse=warehouse, database=database, schema=schema,
        ocsp_fail_open=True, insecure_mode=True,
    )


def _query(sql: str) -> pd.DataFrame:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
        cols = [d.name.lower() for d in cur.description] if cur.description else []
    df = pd.DataFrame(rows, columns=cols)
    # Snowflake returns Decimal as object dtype — coerce to float where possible
    for col in df.columns:
        if df[col].dtype == object:
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass
    return df


@st.cache_data(ttl=3600)
def load_monthly_sales() -> pd.DataFrame:
    return _query(f"SELECT * FROM {_DB}.{_SCHEMA}.MART_MONTHLY_SALES ORDER BY month_start_date")


@st.cache_data(ttl=3600)
def load_top_products() -> pd.DataFrame:
    return _query(f"SELECT * FROM {_DB}.{_SCHEMA}.MART_TOP_PRODUCTS ORDER BY revenue_rank")


@st.cache_data(ttl=3600)
def load_rfm_scored() -> pd.DataFrame:
    return _query(f"SELECT * FROM {_DB}.{_SCHEMA}.MART_CUSTOMER_RFM_SCORED")


@st.cache_data(ttl=3600)
def load_seller_performance() -> pd.DataFrame:
    return _query(f"SELECT * FROM {_DB}.{_SCHEMA}.MART_SELLER_PERFORMANCE ORDER BY revenue_incl_freight DESC")


@st.cache_data(ttl=3600)
def load_delivery_performance() -> pd.DataFrame:
    return _query(f"SELECT * FROM {_DB}.{_SCHEMA}.MART_DELIVERY_PERFORMANCE ORDER BY on_time_delivery_rate DESC")
