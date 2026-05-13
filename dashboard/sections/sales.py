import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import db

_GMV_COLOR = "#D4956A"
_REV_COLOR = "#A35530"
_ACCENT    = "#C47149"
_NEG       = "#A33028"
_LINE      = "#E6E1D4"
_MUTED     = "#6B7480"


def _build_qoq(df: pd.DataFrame) -> list[dict]:
    quarterly = (
        df.groupby(["year_num", "quarter_num"])["revenue_incl_freight"]
        .sum().reset_index()
    )
    quarterly["label"] = quarterly.apply(lambda r: f"Q{int(r.quarter_num)} {int(r.year_num)}", axis=1)
    quarterly["prev"] = quarterly["revenue_incl_freight"].shift(1)
    quarterly["chg"] = (
        (quarterly["revenue_incl_freight"] - quarterly["prev"]) / quarterly["prev"] * 100
    ).round(1)
    return quarterly[["label", "revenue_incl_freight", "chg"]].to_dict("records")


def render():
    monthly  = db.load_monthly_sales()
    products = db.load_top_products()

    st.html("""
    <div class="obi-page-head">
      <div>
        <div class="obi-eyebrow">Section 02 · Commercial</div>
        <h1>Sales &amp; Growth</h1>
        <p class="sub">Compares gross merchandise volume to freight-inclusive revenue, quarterly trajectory, and the category mix that powers growth.</p>
      </div>
      <div class="obi-meta">
        <span class="obi-pill">Lifetime to 2018-09</span>
        <span class="obi-pill">BRL</span>
      </div>
    </div>
    """)

    # ── GMV vs Revenue grouped bar ───────────────────────────────────────────────
    st.html("""
    <div class="obi-panel">
      <div class="obi-panel-head">
        <div>
          <div class="ptitle">Trend</div>
          <h3>Monthly GMV vs. Revenue</h3>
          <p>GMV is item value only. Revenue adds freight charges paid by customers.</p>
        </div>
      </div>
      <div class="obi-panel-body">
    """)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly["month_start_date"], y=monthly["gross_merchandise_value"],
        name="GMV (item value)", marker_color=_GMV_COLOR,
        marker=dict(line=dict(width=0)), width=0.35,
    ))
    fig.add_trace(go.Bar(
        x=monthly["month_start_date"], y=monthly["revenue_incl_freight"],
        name="Revenue (incl. freight)", marker_color=_REV_COLOR,
        marker=dict(line=dict(width=0)), width=0.35,
    ))
    fig.update_layout(
        barmode="group", height=320,
        margin=dict(t=8, r=16, l=0, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        font=dict(family="Manrope, sans-serif", size=11, color=_MUTED),
        legend=dict(orientation="h", y=-0.12, x=0, font=dict(size=12)),
        bargap=0.25, bargroupgap=0.08,
        xaxis=dict(showgrid=False, zeroline=False, tickcolor="rgba(0,0,0,0)", linecolor="rgba(0,0,0,0)"),
        yaxis=dict(showgrid=True, gridcolor=_LINE, zeroline=False, tickcolor="rgba(0,0,0,0)", linecolor="rgba(0,0,0,0)",
                   tickformat="~s", tickprefix="R$"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.html("""
      <div style="font-size:12px;color:var(--muted);margin-top:-8px">
        Freight contributes ~14% of revenue on average
      </div>
      </div></div>
    """)

    # ── QoQ table + Category bars ────────────────────────────────────────────────
    col_left, col_right = st.columns([1, 1])

    with col_left:
        qoq_rows = _build_qoq(monthly)
        max_rev = max(r["revenue_incl_freight"] for r in qoq_rows)

        rows_html = ""
        for i, r in enumerate(qoq_rows):
            rank_cls = "top" if i < 3 else ""
            chg = r["chg"]
            if pd.isna(chg) or chg is None:
                chip = '<span style="font-family:var(--f-mono);color:var(--muted)">—</span>'
            elif chg >= 0:
                chip = f'<span class="obi-chip pos">▲ {chg:.1f}%</span>'
            else:
                chip = f'<span class="obi-chip neg">▼ {abs(chg):.1f}%</span>'

            bar_w = min(100, max(2, (r["revenue_incl_freight"] / max_rev) * 100))
            bar_color = _NEG if (not pd.isna(chg) and chg is not None and chg < 0) else _ACCENT

            rows_html += f"""
            <tr>
              <td><span class="obi-rank {rank_cls}">{str(i+1).zfill(2)}</span> &nbsp; {r['label']}</td>
              <td class="num">R$ {r['revenue_incl_freight']:,.0f}</td>
              <td class="num">{chip}</td>
              <td>
                <div style="display:flex;align-items:center;gap:8px">
                  <div class="obi-bar-track" style="flex:1">
                    <div class="obi-bar-fill" style="width:{bar_w:.0f}%;background:{bar_color}"></div>
                  </div>
                </div>
              </td>
            </tr>"""

        st.html(f"""
        <div class="obi-panel">
          <div class="obi-panel-head">
            <div>
              <div class="ptitle">Cadence</div>
              <h3>Quarter-on-quarter revenue</h3>
              <p>Growth normalized to the prior quarter; — marks the cold start.</p>
            </div>
          </div>
          <div class="obi-panel-body" style="padding:0">
            <table class="obi-table">
              <thead>
                <tr>
                  <th>Quarter</th>
                  <th class="num">Revenue</th>
                  <th class="num">QoQ</th>
                  <th>Velocity</th>
                </tr>
              </thead>
              <tbody>{rows_html}</tbody>
            </table>
          </div>
        </div>
        """)

    with col_right:
        cat = (
            products.groupby("product_category_name_english")["revenue_incl_freight"]
            .sum().sort_values(ascending=False).head(10).reset_index()
        )
        cat["product_category_name_english"] = (
            cat["product_category_name_english"].str.replace("_", " ").str.title()
        )
        max_rev_cat = cat["revenue_incl_freight"].max()
        total_rev_cat = cat["revenue_incl_freight"].sum()

        cat_rows = ""
        for i, row in cat.iterrows():
            rank_cls = "top" if i < 3 else ""
            bar_w = (row["revenue_incl_freight"] / max_rev_cat) * 100
            pct = row["revenue_incl_freight"] / total_rev_cat * 100
            rev_k = row["revenue_incl_freight"]
            rev_fmt = f"R$ {rev_k/1e6:.2f}M" if rev_k >= 1e6 else f"R$ {rev_k/1e3:.0f}K"
            cat_rows += f"""
            <div style="display:grid;grid-template-columns:170px 1fr 80px 60px;gap:12px;align-items:center;margin-bottom:10px">
              <div style="display:flex;align-items:center;gap:8px;font-size:13px;color:var(--ink-2)">
                <span class="obi-rank {rank_cls}">{str(int(i)+1).zfill(2)}</span>
                {row['product_category_name_english']}
              </div>
              <div style="height:10px;background:var(--bg);border-radius:3px;overflow:hidden">
                <div style="height:100%;width:{bar_w:.1f}%;background:linear-gradient(90deg,#A35530 0%,#C47149 100%);border-radius:3px"></div>
              </div>
              <div style="font-family:var(--f-mono);font-size:12px;text-align:right;color:var(--ink-2)">{rev_fmt}</div>
              <div style="font-family:var(--f-mono);font-size:11px;text-align:right;color:var(--muted)">{pct:.1f}%</div>
            </div>"""

        st.html(f"""
        <div class="obi-panel">
          <div class="obi-panel-head">
            <div>
              <div class="ptitle">Category mix</div>
              <h3>Top 10 product categories</h3>
              <p>Ranked by revenue across the full window.</p>
            </div>
          </div>
          <div class="obi-panel-body">{cat_rows}</div>
        </div>
        """)
