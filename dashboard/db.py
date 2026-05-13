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

    if key_path and not password:
        passphrase = os.getenv("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE", "").encode()
        with open(key_path, "rb") as f:
            private_key = load_pem_private_key(f.read(), password=passphrase or None, backend=default_backend())
        private_key_bytes = private_key.private_bytes(
            encoding=Encoding.DER,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption(),
        )
        return snowflake.connector.connect(
            account=account, user=user, role=role, warehouse=warehouse,
            database=database, schema=schema, private_key=private_key_bytes,
        )

    return snowflake.connector.connect(
        account=account, user=user, password=password, role=role,
        warehouse=warehouse, database=database, schema=schema,
    )


def _query(sql: str) -> pd.DataFrame:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
        cols = [d.name for d in cur.description] if cur.description else []
    return pd.DataFrame(rows, columns=cols)


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
