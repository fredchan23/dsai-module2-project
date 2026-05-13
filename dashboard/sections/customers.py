import plotly.express as px
import streamlit as st

import db

_SEGMENT_COLORS = {
    "champions": "#2ecc71",
    "loyal_customers": "#3498db",
    "potential_loyalists": "#9b59b6",
    "recent_customers": "#f1c40f",
    "at_risk": "#e67e22",
    "hibernating": "#e74c3c",
}

_SEGMENT_LABELS = {k: k.replace("_", " ").title() for k in _SEGMENT_COLORS}


def render():
    st.header("Customer Health")

    df = db.load_rfm_scored()
    df["segment_display"] = df["segment_label"].map(_SEGMENT_LABELS)

    states = ["All States"] + sorted(df["customer_state"].dropna().unique().tolist())
    selected_state = st.selectbox("Filter by State", states)

    filtered = df if selected_state == "All States" else df[df["customer_state"] == selected_state]

    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("RFM Scatter: Recency vs Frequency")
        fig_scatter = px.scatter(
            filtered,
            x="recency_days",
            y="frequency_orders",
            size="monetary_value",
            color="segment_display",
            color_discrete_map={v: _SEGMENT_COLORS[k] for k, v in _SEGMENT_LABELS.items()},
            hover_data={"monetary_value": ":,.0f", "recency_days": True, "frequency_orders": True},
            labels={
                "recency_days": "Recency (days since last order)",
                "frequency_orders": "Frequency (# orders)",
                "segment_display": "Segment",
                "monetary_value": "Monetary Value (R$)",
            },
            template="plotly_white",
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col2:
        st.subheader("Segment Distribution")
        seg_counts = filtered["segment_display"].value_counts().reset_index()
        seg_counts.columns = ["Segment", "Customers"]
        fig_donut = px.pie(
            seg_counts,
            names="Segment",
            values="Customers",
            hole=0.45,
            color="Segment",
            color_discrete_map={v: _SEGMENT_COLORS[k] for k, v in _SEGMENT_LABELS.items()},
            template="plotly_white",
        )
        fig_donut.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_donut, use_container_width=True)

    st.subheader("Segment Summary")
    summary = (
        filtered.groupby("segment_display")
        .agg(
            Customers=("customer_unique_id", "count"),
            Avg_Monetary=("monetary_value", "mean"),
            Avg_Recency=("recency_days", "mean"),
            Avg_Frequency=("frequency_orders", "mean"),
        )
        .reset_index()
        .rename(columns={
            "segment_display": "Segment",
            "Avg_Monetary": "Avg Monetary (R$)",
            "Avg_Recency": "Avg Recency (days)",
            "Avg_Frequency": "Avg Orders",
        })
        .sort_values("Customers", ascending=False)
    )
    summary["Avg Monetary (R$)"] = summary["Avg Monetary (R$)"].map(lambda v: f"R$ {v:,.0f}")
    summary["Avg Recency (days)"] = summary["Avg Recency (days)"].map(lambda v: f"{v:.0f}")
    summary["Avg Orders"] = summary["Avg Orders"].map(lambda v: f"{v:.1f}")
    st.dataframe(summary, use_container_width=True, hide_index=True)
