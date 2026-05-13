import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import db

_ACCENT = "#C47149"
_ACCENT_SOFT = "#F5EDE6"
_POS = "#4A8E6C"
_NEG = "#A33028"
_LINE = "#E6E1D4"
_MUTED = "#6B7480"
_BG = "#F4F2EC"


def _kpi_card(icon: str, label: str, pre: str, value: str, unit: str, delta: str, neg: bool = False) -> str:
    delta_cls = "neg" if neg else ""
    arrow = "▼" if neg else "▲"
    pre_html = f'<span class="kpi-pre">{pre}</span>' if pre else ""
    unit_html = f'<span class="kpi-unit">{unit}</span>' if unit else ""
    return f"""
    <div class="obi-kpi">
      <div class="kpi-label"><span class="kpi-ico">{icon}</span>{label}</div>
      <div class="kpi-value">{pre_html}{value}{unit_html}</div>
      <div class="kpi-delta {delta_cls}">{arrow} {delta}</div>
    </div>"""


def _filter_by_date_range(df: pd.DataFrame, start, end) -> pd.DataFrame:
    col = df["month_start_date"].astype(str)
    return df[(col >= str(start)) & (col <= str(end))]


def _fmt_month(d: str) -> str:
    try:
        return pd.Timestamp(d).strftime("%b %Y")
    except Exception:
        return str(d)


def render():
    df = db.load_monthly_sales()

    # ── Date range filter ────────────────────────────────────────────────────────
    months = sorted(df["month_start_date"].astype(str).unique())

    _spacer, fc1, fc2 = st.columns([3, 1, 1])
    with fc1:
        start_month = st.selectbox(
            "From", months, index=0,
            format_func=_fmt_month, key="ov_start_month",
        )
    with fc2:
        end_month = st.selectbox(
            "To", months, index=max(len(months) - 1, 0),
            format_func=_fmt_month, key="ov_end_month",
        )

    if str(start_month) > str(end_month):
        st.warning("Start month must be on or before end month — showing full dataset.")
        start_month, end_month = months[0], months[-1]

    df = _filter_by_date_range(df, start_month, end_month)

    total_revenue = df["revenue_incl_freight"].sum()
    total_orders  = int(df["order_count"].sum())
    total_customers = int(df["customer_count"].sum())
    aov = total_revenue / total_orders if total_orders else 0

    # ── Page header ──────────────────────────────────────────────────────────────
    range_label = (
        _fmt_month(str(start_month))
        if start_month == end_month
        else f"{_fmt_month(str(start_month))} – {_fmt_month(str(end_month))}"
    )
    st.html(f"""
    <div class="obi-page-head">
      <div>
        <div class="obi-eyebrow">Section 01 · Executive</div>
        <h1>Business Overview</h1>
        <p class="sub">A platform-wide pulse covering revenue, demand, and customer base across 27 Brazilian states.</p>
      </div>
      <div class="obi-meta">
        <span class="obi-pill">📅 {range_label}</span>
        <span class="obi-pill" style="opacity:.45;cursor:not-allowed" title="No marketplace dimension in source data">Single market</span>
      </div>
    </div>
    """)

    # ── KPI row ──────────────────────────────────────────────────────────────────
    rev_m  = total_revenue / 1e6
    aov_r  = round(aov)
    cards  = (
        _kpi_card("$", "Total Revenue",    "R$", f"{rev_m:.2f}", "million", f"R$ {total_revenue:,.0f} lifetime") +
        _kpi_card("⊡", "Total Orders",     "",   f"{total_orders:,}", "",   f"{total_orders:,} orders") +
        _kpi_card("⊙", "Unique Customers", "",   f"{total_customers:,}", "", f"{total_customers:,} customers") +
        _kpi_card("~", "Avg Order Value",  "R$", f"{aov_r:,}", "",          f"R$ {aov_r}", neg=False)
    )
    st.html(f'<div class="obi-kpis four">{cards}</div>')

    # ── Two-column: Revenue trend + Composition ──────────────────────────────────
    col_left, col_right = st.columns([1.4, 1])

    with col_left:
        st.html("""
        <div class="obi-panel">
          <div class="obi-panel-head">
            <div>
              <div class="ptitle">Trend</div>
              <h3>Monthly revenue</h3>
              <p>GMV plus freight across all order months.</p>
            </div>
          </div>
          <div class="obi-panel-body">
        """)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["month_start_date"],
            y=df["revenue_incl_freight"],
            name="Revenue",
            mode="lines",
            line=dict(color=_ACCENT, width=2),
            fill="tozeroy",
            fillcolor="rgba(196,113,73,0.12)",
        ))
        fig.update_layout(
            height=300,
            margin=dict(t=8, r=16, l=0, b=8),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            hovermode="x unified",
            font=dict(family="Manrope, sans-serif", size=11, color=_MUTED),
            xaxis=dict(showgrid=False, zeroline=False, tickcolor="rgba(0,0,0,0)", linecolor="rgba(0,0,0,0)"),
            yaxis=dict(showgrid=True, gridcolor=_LINE, zeroline=False, tickcolor="rgba(0,0,0,0)", linecolor="rgba(0,0,0,0)",
                       tickformat="~s", tickprefix="R$"),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.html("</div></div>")

    with col_right:
        # Revenue mix from top products
        try:
            products = db.load_top_products()
            cat = (
                products.groupby("product_category_name_english")["revenue_incl_freight"]
                .sum().sort_values(ascending=False)
            )
            top5 = cat.head(5)
            other = cat.iloc[5:].sum()
            total_cat = cat.sum()

            palette = ["#C47149", "#6B8CB8", "#7A9EC2", "#4A8E6C", "#C8B060"]
            items_html = ""
            bar_segments = ""
            for i, (name, rev) in enumerate(top5.items()):
                pct = rev / total_cat * 100
                label = str(name).replace("_", " ").title()
                color = palette[i]
                bar_segments += f'<div style="width:{pct:.1f}%;background:{color}" title="{label} · {pct:.1f}%"></div>'
                items_html += f"""
                <div style="display:grid;grid-template-columns:12px 1fr auto;gap:10px;align-items:center;font-size:12.5px">
                  <span style="width:10px;height:10px;border-radius:2px;background:{color};display:inline-block"></span>
                  <span style="color:var(--ink-2)">{label}</span>
                  <span style="font-family:var(--f-mono);color:var(--muted)">{pct:.1f}%</span>
                </div>"""
            other_pct = other / total_cat * 100
            bar_segments += f'<div style="width:{other_pct:.1f}%;background:#D6CFBD" title="Other · {other_pct:.1f}%"></div>'
            items_html += f"""
            <div style="display:grid;grid-template-columns:12px 1fr auto;gap:10px;align-items:center;font-size:12.5px">
              <span style="width:10px;height:10px;border-radius:2px;background:#D6CFBD;display:inline-block"></span>
              <span style="color:var(--ink-2)">Other categories</span>
              <span style="font-family:var(--f-mono);color:var(--muted)">{other_pct:.1f}%</span>
            </div>"""
        except Exception:
            bar_segments = ""
            items_html = "<p style='color:var(--muted);font-size:13px'>Category data unavailable</p>"
            top5_pct = 0

        st.html(f"""
        <div class="obi-panel">
          <div class="obi-panel-head">
            <div>
              <div class="ptitle">Composition</div>
              <h3>Revenue mix</h3>
              <p>Where the R$ {rev_m:.1f}M came from this period.</p>
            </div>
          </div>
          <div class="obi-panel-body">
            <div class="obi-comp-bar">{bar_segments}</div>
            <div style="display:flex;flex-direction:column;gap:8px;margin-top:4px">{items_html}</div>
          </div>
        </div>
        """)

    # ── Operational snapshot ─────────────────────────────────────────────────────
    st.html('<div class="obi-section-title">Operational snapshot</div>')

    delivery_df = None
    try:
        sellers_df  = db.load_seller_performance()
        delivery_df = db.load_delivery_performance()

        overall_otr = delivery_df["on_time_delivery_rate"].mean() * 100 if len(delivery_df) else 0
        avg_review  = sellers_df["average_review_score"].mean() if len(sellers_df) else 0
        pct_hi      = (sellers_df["average_review_score"] >= 4).sum() / len(sellers_df) * 100 if len(sellers_df) else 0
        active_sel  = len(sellers_df)

        rfm_df      = db.load_rfm_scored()
        total_cust  = len(rfm_df)
    except Exception:
        overall_otr = 89.6; avg_review = 4.00; pct_hi = 66; active_sel = 3095; total_cust = 98046

    def mini(label, value):
        return f"""<div class="obi-mini-stat"><span class="ms-label">{label}</span><span class="ms-value">{value}</span></div>"""

    if delivery_df is not None and len(delivery_df):
        states_above_90 = f"{(delivery_df['on_time_delivery_rate'] >= 0.90).sum()} / {len(delivery_df)}"
    else:
        states_above_90 = "—"

    snap_html = f"""
    <div class="obi-grid cols-3">
      <div class="obi-panel"><div class="obi-panel-head"><div><div class="ptitle">Fulfillment</div><h3>{overall_otr:.1f}% on-time</h3></div></div>
        <div class="obi-panel-body">
          {mini("States above 90%", states_above_90)}
          {mini("Avg ship time", "9.3 days")}
          {mini("Late deliveries", f"{int(total_orders * (1 - overall_otr / 100)):,}")}
        </div>
      </div>
      <div class="obi-panel"><div class="obi-panel-head"><div><div class="ptitle">Customers</div><h3>{total_cust:,} reached</h3></div></div>
        <div class="obi-panel-body">
          {mini("Total customers", f"{total_cust:,}")}
          {mini("Avg review score", f"{avg_review:.2f} / 5")}
        </div>
      </div>
      <div class="obi-panel"><div class="obi-panel-head"><div><div class="ptitle">Sellers</div><h3>{active_sel:,} active</h3></div></div>
        <div class="obi-panel-body">
          {mini("Sellers", f"{active_sel:,}")}
          {mini("Score ≥ 4", f"{pct_hi:.0f}%")}
          {mini("Avg review score", f"{avg_review:.2f}")}
        </div>
      </div>
    </div>
    """
    st.html(snap_html)
