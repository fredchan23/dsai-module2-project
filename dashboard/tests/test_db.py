"""Tests for Task 2: Snowflake connection layer (db.py).

Live Snowflake tests are skipped unless SNOWFLAKE_ACCOUNT is set in the environment.
Unit tests mock the connector and verify the module structure.
"""
import importlib
import os
import sys
import unittest.mock as mock

import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# --- Module structure tests (always run) ---

def test_db_module_exists():
    path = os.path.join(os.path.dirname(__file__), "..", "db.py")
    assert os.path.isfile(path), "dashboard/db.py must exist"


def test_db_exposes_get_connection():
    import db
    assert hasattr(db, "get_connection"), "db.py must expose get_connection()"


def test_db_exposes_all_load_functions():
    import db
    for fn in ["load_monthly_sales", "load_top_products", "load_rfm_scored",
               "load_seller_performance", "load_delivery_performance"]:
        assert hasattr(db, fn), f"db.py must expose {fn}()"
        assert callable(getattr(db, fn)), f"{fn} must be callable"


# --- Unit tests with mocked connector ---

def _make_mock_conn(rows, columns):
    """Return a mock snowflake connection whose cursor yields given rows/columns."""
    cursor = mock.MagicMock()
    cursor.fetchall.return_value = rows
    cursor.description = [mock.MagicMock(name=c) for c in columns]
    for i, col in enumerate(columns):
        cursor.description[i].name = col
    conn = mock.MagicMock()
    conn.cursor.return_value.__enter__ = lambda s: cursor
    conn.cursor.return_value.__exit__ = mock.MagicMock(return_value=False)
    return conn, cursor


def test_load_monthly_sales_returns_dataframe(monkeypatch):
    import db
    fake_rows = [("2023-01-01", 2023, 1, 1, "January", 100, 80, 90, 50000.0, 55000.0, 550.0)]
    fake_cols = ["month_start_date", "year_num", "quarter_num", "month_num", "month_name",
                 "order_count", "customer_count", "delivered_order_count",
                 "gross_merchandise_value", "revenue_incl_freight", "average_order_value"]
    conn, _ = _make_mock_conn(fake_rows, fake_cols)
    monkeypatch.setattr(db, "get_connection", lambda: conn)
    # Clear cache so monkeypatch takes effect
    db.load_monthly_sales.clear()
    result = db.load_monthly_sales()
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == fake_cols
    assert len(result) == 1


def test_load_rfm_scored_returns_dataframe(monkeypatch):
    import db
    fake_rows = [("cust1", "SP", "2022-01-01", "2023-06-01", 30, 3, 1500.0, 500.0,
                  "2023-06-01", 4, 3, 4, "434", "champions")]
    fake_cols = ["customer_unique_id", "customer_state", "first_order_date", "last_order_date",
                 "recency_days", "frequency_orders", "monetary_value", "average_order_value",
                 "rfm_snapshot_date", "recency_score", "frequency_score", "monetary_score",
                 "rfm_score_code", "segment_label"]
    conn, _ = _make_mock_conn(fake_rows, fake_cols)
    monkeypatch.setattr(db, "get_connection", lambda: conn)
    db.load_rfm_scored.clear()
    result = db.load_rfm_scored()
    assert isinstance(result, pd.DataFrame)
    assert "segment_label" in result.columns


def test_load_functions_use_correct_tables(monkeypatch):
    """Each load_* must query its corresponding mart table."""
    import db

    queries_issued = []

    def fake_conn():
        cursor = mock.MagicMock()
        cursor.fetchall.return_value = []
        cursor.description = []
        cursor.execute.side_effect = lambda q: queries_issued.append(q)
        conn = mock.MagicMock()
        conn.cursor.return_value.__enter__ = lambda s: cursor
        conn.cursor.return_value.__exit__ = mock.MagicMock(return_value=False)
        return conn

    expected = {
        "load_monthly_sales": "MART_MONTHLY_SALES",
        "load_top_products": "MART_TOP_PRODUCTS",
        "load_rfm_scored": "MART_CUSTOMER_RFM_SCORED",
        "load_seller_performance": "MART_SELLER_PERFORMANCE",
        "load_delivery_performance": "MART_DELIVERY_PERFORMANCE",
    }
    monkeypatch.setattr(db, "get_connection", fake_conn)
    for fn_name, table in expected.items():
        queries_issued.clear()
        fn = getattr(db, fn_name)
        fn.clear()
        fn()
        assert any(table in q.upper() for q in queries_issued), \
            f"{fn_name}() must query {table}"


# --- Live integration test (skipped without credentials) ---

@pytest.mark.skipif(
    not os.environ.get("SNOWFLAKE_ACCOUNT"),
    reason="SNOWFLAKE_ACCOUNT not set — skipping live Snowflake test"
)
def test_live_load_monthly_sales():
    import db
    db.load_monthly_sales.clear()
    df = db.load_monthly_sales()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0, "mart_monthly_sales must return rows"
    assert "revenue_incl_freight" in df.columns
