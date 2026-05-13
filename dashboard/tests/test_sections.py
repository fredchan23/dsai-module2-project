"""Tests for Tasks 3–6: section render functions using mocked data."""
import os
import sys
import unittest.mock as mock

import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ---------------------------------------------------------------------------
# Fixtures: sample DataFrames matching real mart schemas
# ---------------------------------------------------------------------------

@pytest.fixture
def monthly_sales_df():
    return pd.DataFrame([
        {"month_start_date": "2022-01-01", "year_num": 2022, "quarter_num": 1,
         "month_num": 1, "month_name": "January", "order_count": 100,
         "customer_count": 90, "delivered_order_count": 85,
         "gross_merchandise_value": 40000.0, "revenue_incl_freight": 45000.0,
         "average_order_value": 450.0},
        {"month_start_date": "2022-02-01", "year_num": 2022, "quarter_num": 1,
         "month_num": 2, "month_name": "February", "order_count": 120,
         "customer_count": 110, "delivered_order_count": 105,
         "gross_merchandise_value": 50000.0, "revenue_incl_freight": 56000.0,
         "average_order_value": 466.7},
    ])


@pytest.fixture
def top_products_df():
    return pd.DataFrame([
        {"product_id": "p1", "product_category_name_english": "bed_bath_table",
         "order_count": 50, "units_sold": 60, "gross_merchandise_value": 3000.0,
         "revenue_incl_freight": 3500.0, "average_unit_revenue": 58.3,
         "revenue_rank": 1, "category_revenue_rank": 1},
        {"product_id": "p2", "product_category_name_english": "sports_leisure",
         "order_count": 40, "units_sold": 45, "gross_merchandise_value": 2000.0,
         "revenue_incl_freight": 2200.0, "average_unit_revenue": 48.9,
         "revenue_rank": 2, "category_revenue_rank": 1},
    ])


@pytest.fixture
def rfm_df():
    return pd.DataFrame([
        {"customer_unique_id": "c1", "customer_state": "SP",
         "first_order_date": "2021-01-01", "last_order_date": "2023-05-01",
         "recency_days": 30, "frequency_orders": 5, "monetary_value": 2000.0,
         "average_order_value": 400.0, "rfm_snapshot_date": "2023-06-01",
         "recency_score": 4, "frequency_score": 4, "monetary_score": 4,
         "rfm_score_code": "444", "segment_label": "champions"},
        {"customer_unique_id": "c2", "customer_state": "RJ",
         "first_order_date": "2020-06-01", "last_order_date": "2022-01-01",
         "recency_days": 500, "frequency_orders": 2, "monetary_value": 500.0,
         "average_order_value": 250.0, "rfm_snapshot_date": "2023-06-01",
         "recency_score": 1, "frequency_score": 1, "monetary_score": 1,
         "rfm_score_code": "111", "segment_label": "hibernating"},
    ])


@pytest.fixture
def seller_df():
    return pd.DataFrame([
        {"seller_id": "s1", "seller_state": "SP", "first_order_date": "2021-01-01",
         "last_order_date": "2023-06-01", "order_count": 200, "items_sold": 250,
         "gross_merchandise_value": 80000.0, "revenue_incl_freight": 90000.0,
         "average_order_revenue": 450.0, "eligible_delivery_order_count": 180,
         "on_time_delivery_order_count": 160, "on_time_delivery_rate": 0.89,
         "average_delivery_days": 8.5, "average_days_to_ship": 2.1,
         "average_review_score": 4.2, "low_score_review_rate": 0.05},
    ])


@pytest.fixture
def delivery_df():
    return pd.DataFrame([
        {"customer_state": "SP", "eligible_delivery_order_count": 5000,
         "on_time_delivery_order_count": 4600, "late_delivery_order_count": 400,
         "on_time_delivery_rate": 0.92, "avg_delivery_days": 7.2},
        {"customer_state": "RJ", "eligible_delivery_order_count": 2000,
         "on_time_delivery_order_count": 1500, "late_delivery_order_count": 500,
         "on_time_delivery_rate": 0.75, "avg_delivery_days": 9.1},
        {"customer_state": "BA", "eligible_delivery_order_count": 800,
         "on_time_delivery_order_count": 520, "late_delivery_order_count": 280,
         "on_time_delivery_rate": 0.65, "avg_delivery_days": 12.3},
    ])


# ---------------------------------------------------------------------------
# Helper: patch st.* calls so tests don't need a real Streamlit session
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def mock_streamlit():
    st_mock = mock.MagicMock()
    col_mocks = []

    def _columns(spec):
        n = len(spec) if hasattr(spec, "__len__") else int(spec)
        cols = [mock.MagicMock() for _ in range(n)]
        col_mocks.extend(cols)
        return cols

    st_mock.columns.side_effect = _columns
    st_mock.selectbox.return_value = "All States"
    st_mock._col_mocks = col_mocks

    with mock.patch.dict("sys.modules", {"streamlit": st_mock}):
        yield


def _metric_called_anywhere(st_mock) -> bool:
    """True if metric() was called on st or any column mock returned by st.columns."""
    if st_mock.metric.called:
        return True
    return any(c.metric.called for c in st_mock._col_mocks)


def _metric_call_count(st_mock) -> int:
    total = st_mock.metric.call_count
    for c in st_mock._col_mocks:
        total += c.metric.call_count
    return total


# ---------------------------------------------------------------------------
# Task 3: Overview section
# ---------------------------------------------------------------------------

def test_overview_render_callable():
    import importlib
    mod = importlib.import_module("sections.overview")
    assert callable(mod.render)


def test_overview_calls_st_metric(monthly_sales_df, mock_streamlit):
    import streamlit as st
    import sys
    for key in list(sys.modules.keys()):
        if "sections.overview" in key:
            del sys.modules[key]
    with mock.patch("db.load_monthly_sales", return_value=monthly_sales_df):
        import sections.overview as ov
        ov.render()
    assert _metric_called_anywhere(st), "Overview must call st.metric (or column.metric)"


def test_overview_displays_four_kpis(monthly_sales_df, mock_streamlit):
    import streamlit as st
    import sys
    for key in list(sys.modules.keys()):
        if "sections.overview" in key:
            del sys.modules[key]
    with mock.patch("db.load_monthly_sales", return_value=monthly_sales_df):
        import sections.overview as ov
        ov.render()
    assert _metric_call_count(st) >= 4, "Overview must display at least 4 KPI metrics"


# ---------------------------------------------------------------------------
# Task 4: Sales & Growth section
# ---------------------------------------------------------------------------

def test_sales_render_callable():
    import importlib
    mod = importlib.import_module("sections.sales")
    assert callable(mod.render)


def test_sales_calls_plotly_chart(monthly_sales_df, top_products_df):
    import streamlit as st
    import sys
    for key in list(sys.modules.keys()):
        if "sections.sales" in key:
            del sys.modules[key]
    with mock.patch("db.load_monthly_sales", return_value=monthly_sales_df), \
         mock.patch("db.load_top_products", return_value=top_products_df):
        import sections.sales as s
        s.render()
    st.plotly_chart.assert_called()


def test_sales_qoq_table_shown(monthly_sales_df, top_products_df):
    import streamlit as st
    import sys
    for key in list(sys.modules.keys()):
        if "sections.sales" in key:
            del sys.modules[key]
    with mock.patch("db.load_monthly_sales", return_value=monthly_sales_df), \
         mock.patch("db.load_top_products", return_value=top_products_df):
        import sections.sales as s
        s.render()
    # st.dataframe or st.table should be called for QoQ table
    assert st.dataframe.called or st.table.called, "Sales section must render a QoQ table"


# ---------------------------------------------------------------------------
# Task 5: Customer RFM section
# ---------------------------------------------------------------------------

def test_customers_render_callable():
    import importlib
    mod = importlib.import_module("sections.customers")
    assert callable(mod.render)


def test_customers_renders_scatter_and_donut(rfm_df):
    import streamlit as st
    import sys
    for key in list(sys.modules.keys()):
        if "sections.customers" in key:
            del sys.modules[key]
    with mock.patch("db.load_rfm_scored", return_value=rfm_df):
        import sections.customers as c
        c.render()
    assert st.plotly_chart.call_count >= 2, "Customers section must render scatter + donut (2 charts)"


def test_customers_state_filter_present(rfm_df):
    import streamlit as st
    import sys
    for key in list(sys.modules.keys()):
        if "sections.customers" in key:
            del sys.modules[key]
    with mock.patch("db.load_rfm_scored", return_value=rfm_df):
        import sections.customers as c
        c.render()
    assert st.selectbox.called, "Customers section must have a state selectbox filter"


# ---------------------------------------------------------------------------
# Task 6: Seller & Delivery section
# ---------------------------------------------------------------------------

def test_sellers_render_callable():
    import importlib
    mod = importlib.import_module("sections.sellers")
    assert callable(mod.render)


def test_sellers_renders_table_and_chart(seller_df, delivery_df):
    import streamlit as st
    import sys
    for key in list(sys.modules.keys()):
        if "sections.sellers" in key:
            del sys.modules[key]
    with mock.patch("db.load_seller_performance", return_value=seller_df), \
         mock.patch("db.load_delivery_performance", return_value=delivery_df):
        import sections.sellers as s
        s.render()
    assert st.dataframe.called, "Sellers section must render seller performance table"
    assert st.plotly_chart.called, "Sellers section must render delivery rate chart"


def test_sellers_renders_kpi_row(seller_df, delivery_df, mock_streamlit):
    import streamlit as st
    import sys
    for key in list(sys.modules.keys()):
        if "sections.sellers" in key:
            del sys.modules[key]
    with mock.patch("db.load_seller_performance", return_value=seller_df), \
         mock.patch("db.load_delivery_performance", return_value=delivery_df):
        import sections.sellers as s
        s.render()
    assert _metric_called_anywhere(st), "Sellers section must render KPI metrics"
