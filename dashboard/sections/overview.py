import plotly.express as px
import streamlit as st

import db

_BRL = "R$"


def _fmt_currency(val: float) -> str:
    return f"{_BRL} {val:,.0f}"


def render():
    st.header("Business Overview")

    df = db.load_monthly_sales()

    total_revenue = df["revenue_incl_freight"].sum()
    total_orders = int(df["order_count"].sum())
    total_customers = int(df["customer_count"].sum())
    aov = total_revenue / total_orders if total_orders else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", _fmt_currency(total_revenue))
    c2.metric("Total Orders", f"{total_orders:,}")
    c3.metric("Unique Customers", f"{total_customers:,}")
    c4.metric("Avg Order Value", _fmt_currency(aov))

    st.markdown("---")
    st.subheader("Monthly Revenue Trend")

    fig = px.line(
        df,
        x="month_start_date",
        y="revenue_incl_freight",
        labels={"month_start_date": "Month", "revenue_incl_freight": f"Revenue ({_BRL})"},
        template="plotly_white",
    )
    fig.update_traces(line_color="#1f77b4", line_width=2)
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
