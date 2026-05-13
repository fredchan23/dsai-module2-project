import plotly.express as px
import streamlit as st

import db

_BRL = "R$"


def _delivery_color(rate: float) -> str:
    if rate >= 0.90:
        return "#2ecc71"
    if rate >= 0.70:
        return "#f39c12"
    return "#e74c3c"


def render():
    st.header("Seller & Delivery")

    sellers = db.load_seller_performance()
    delivery = db.load_delivery_performance()

    # KPI row
    overall_otd = delivery["on_time_delivery_rate"].mean() if len(delivery) else 0
    avg_review = sellers["average_review_score"].mean() if len(sellers) else 0
    pct_high_review = (
        (sellers["average_review_score"] >= 4).sum() / len(sellers) * 100
        if len(sellers) else 0
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Overall On-Time Delivery", f"{overall_otd:.1%}")
    c2.metric("Avg Seller Review Score", f"{avg_review:.2f} / 5.0")
    c3.metric("Sellers with Score ≥ 4", f"{pct_high_review:.0f}%")

    st.markdown("---")

    # Seller performance table (top 50 by revenue)
    st.subheader("Top 50 Sellers by Revenue")
    table_df = sellers.head(50).copy()
    table_df["seller_id_short"] = table_df["seller_id"].str[:12] + "..."
    display_cols = {
        "seller_id_short": "Seller ID",
        "seller_state": "State",
        "order_count": "Orders",
        "revenue_incl_freight": f"Revenue ({_BRL})",
        "on_time_delivery_rate": "On-Time Rate",
        "average_review_score": "Avg Review",
    }
    display_df = table_df[list(display_cols.keys())].rename(columns=display_cols)
    display_df[f"Revenue ({_BRL})"] = display_df[f"Revenue ({_BRL})"].map(lambda v: f"{_BRL} {v:,.0f}")
    display_df["On-Time Rate"] = display_df["On-Time Rate"].map(lambda v: f"{v:.1%}")
    display_df["Avg Review"] = display_df["Avg Review"].map(lambda v: f"{v:.2f}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # On-time delivery rate by state
    st.subheader("On-Time Delivery Rate by State")
    delivery_sorted = delivery.sort_values("on_time_delivery_rate", ascending=True)
    delivery_sorted["color"] = delivery_sorted["on_time_delivery_rate"].map(_delivery_color)

    fig = px.bar(
        delivery_sorted,
        x="on_time_delivery_rate",
        y="customer_state",
        orientation="h",
        color="on_time_delivery_rate",
        color_continuous_scale=[[0, "#e74c3c"], [0.70, "#f39c12"], [0.90, "#2ecc71"], [1.0, "#27ae60"]],
        range_color=[0, 1],
        labels={"on_time_delivery_rate": "On-Time Rate", "customer_state": "State"},
        template="plotly_white",
    )
    fig.update_layout(coloraxis_showscale=False)
    fig.update_xaxes(tickformat=".0%", range=[0, 1])
    st.plotly_chart(fig, use_container_width=True)
