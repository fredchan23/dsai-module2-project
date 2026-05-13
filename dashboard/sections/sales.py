import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import db

_BRL = "R$"


def _build_qoq(df: pd.DataFrame) -> pd.DataFrame:
    quarterly = (
        df.groupby(["year_num", "quarter_num"])["revenue_incl_freight"]
        .sum()
        .reset_index()
    )
    quarterly["label"] = quarterly.apply(lambda r: f"Q{int(r.quarter_num)} {int(r.year_num)}", axis=1)
    quarterly["prev_revenue"] = quarterly["revenue_incl_freight"].shift(1)
    quarterly["qoq_pct"] = (
        (quarterly["revenue_incl_freight"] - quarterly["prev_revenue"])
        / quarterly["prev_revenue"]
        * 100
    ).round(1)
    quarterly["qoq_display"] = quarterly["qoq_pct"].apply(
        lambda v: "—" if pd.isna(v) else f"{v:+.1f}%"
    )
    return quarterly[["label", "revenue_incl_freight", "qoq_display"]].rename(
        columns={"label": "Quarter", "revenue_incl_freight": f"Revenue ({_BRL})", "qoq_display": "QoQ Change"}
    )


def render():
    st.header("Sales & Growth")

    monthly = db.load_monthly_sales()
    products = db.load_top_products()

    # GMV vs Revenue chart
    st.subheader("Monthly GMV vs Revenue")
    fig_gmv = go.Figure()
    fig_gmv.add_trace(go.Bar(
        x=monthly["month_start_date"], y=monthly["gross_merchandise_value"],
        name="GMV", marker_color="#aec7e8",
    ))
    fig_gmv.add_trace(go.Bar(
        x=monthly["month_start_date"], y=monthly["revenue_incl_freight"],
        name=f"Revenue (incl. freight)", marker_color="#1f77b4",
    ))
    fig_gmv.update_layout(barmode="group", template="plotly_white",
                          xaxis_title="Month", yaxis_title=f"Amount ({_BRL})",
                          hovermode="x unified")
    st.plotly_chart(fig_gmv, use_container_width=True)

    # QoQ table
    st.subheader("Quarter-on-Quarter Revenue")
    qoq_df = _build_qoq(monthly)
    qoq_df[f"Revenue ({_BRL})"] = qoq_df[f"Revenue ({_BRL})"].map(lambda v: f"{_BRL} {v:,.0f}")
    st.dataframe(qoq_df, use_container_width=True, hide_index=True)

    # Top 10 categories
    st.subheader("Top 10 Product Categories by Revenue")
    cat_df = (
        products.groupby("product_category_name_english")["revenue_incl_freight"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    cat_df["product_category_name_english"] = cat_df["product_category_name_english"].str.replace("_", " ").str.title()
    fig_cat = px.bar(
        cat_df.sort_values("revenue_incl_freight"),
        x="revenue_incl_freight",
        y="product_category_name_english",
        orientation="h",
        labels={"revenue_incl_freight": f"Revenue ({_BRL})", "product_category_name_english": "Category"},
        template="plotly_white",
        color_discrete_sequence=["#1f77b4"],
    )
    st.plotly_chart(fig_cat, use_container_width=True)
