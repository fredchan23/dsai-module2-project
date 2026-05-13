import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import db

_SEG_COLORS = {
    "champions":          "#4A8E6C",
    "loyal_customers":    "#6B8CB8",
    "potential_loyalists":"#7A9EC2",
    "recent_customers":   "#C8B060",
    "at_risk":            "#C47149",
    "hibernating":        "#A33028",
}
_SEG_LABELS = {k: k.replace("_", " ").title() for k in _SEG_COLORS}
_LINE  = "#E6E1D4"
_MUTED = "#6B7480"


def render():
    df = db.load_rfm_scored()
    df["seg_display"] = df["segment_label"].map(_SEG_LABELS)
    df["seg_color"]   = df["segment_label"].map(_SEG_COLORS)

    states = ["All states"] + sorted(df["customer_state"].dropna().unique().tolist())

    st.html("""
    <div class="obi-page-head">
      <div>
        <div class="obi-eyebrow">Section 03 · CRM</div>
        <h1>Customer Health</h1>
        <p class="sub">RFM segmentation across the active base — recency, frequency, monetary value — sized by spend.</p>
      </div>
    """)

    # State filter inline in the page meta
    selected_state = st.selectbox(
        "Filter by state",
        states,
        label_visibility="collapsed",
    )
    st.html("</div>")

    filtered = df if selected_state == "All states" else df[df["customer_state"] == selected_state]

    total = len(filtered)
    champ_pct = len(filtered[filtered["segment_label"] == "champions"]) / total * 100 if total else 0
    risk_pct  = len(filtered[filtered["segment_label"] == "at_risk"])   / total * 100 if total else 0

    # ── KPIs ─────────────────────────────────────────────────────────────────────
    kpis_html = f"""
    <div class="obi-kpis three">
      <div class="obi-kpi">
        <div class="kpi-label"><span class="kpi-ico">⊙</span>Active Customers</div>
        <div class="kpi-value">{total:,}</div>
        <div class="kpi-delta">▲ {selected_state}</div>
      </div>
      <div class="obi-kpi">
        <div class="kpi-label"><span class="kpi-ico">★</span>Champions Share</div>
        <div class="kpi-value">{champ_pct:.1f}<span class="kpi-unit">%</span></div>
        <div class="kpi-delta">▲ of customers</div>
      </div>
      <div class="obi-kpi">
        <div class="kpi-label"><span class="kpi-ico">⚠</span>At-Risk Share</div>
        <div class="kpi-value">{risk_pct:.1f}<span class="kpi-unit">%</span></div>
        <div class="kpi-delta neg">▼ of customers</div>
      </div>
    </div>
    """
    st.html(kpis_html)

    # ── Scatter + Donut ──────────────────────────────────────────────────────────
    col_left, col_right = st.columns([1, 1])

    color_map = {v: _SEG_COLORS[k] for k, v in _SEG_LABELS.items()}

    with col_left:
        st.html("""
        <div class="obi-panel">
          <div class="obi-panel-head">
            <div>
              <div class="ptitle">RFM</div>
              <h3>Recency vs. frequency</h3>
              <p>Each dot is one customer, sized by spend, colored by segment.</p>
            </div>
          </div>
          <div class="obi-panel-body">
        """)

        sample = filtered.sample(min(2000, len(filtered)), random_state=42) if len(filtered) > 2000 else filtered
        fig = px.scatter(
            sample,
            x="recency_days",
            y="frequency_orders",
            size="monetary_value",
            color="seg_display",
            color_discrete_map=color_map,
            hover_data={"monetary_value": ":,.0f"},
            labels={
                "recency_days":    "Recency (days since last order)",
                "frequency_orders":"Frequency (# orders)",
                "seg_display":     "Segment",
                "monetary_value":  "Spend (R$)",
            },
            size_max=18,
            opacity=0.55,
            template="none",
        )
        fig.update_layout(
            height=360,
            margin=dict(t=8, r=16, l=8, b=40),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Manrope, sans-serif", size=11, color=_MUTED),
            legend=dict(title="", font=dict(size=11), y=1, x=1, xanchor="right", yanchor="top"),
            xaxis=dict(showgrid=True, gridcolor=_LINE, zeroline=False, tickcolor="rgba(0,0,0,0)", linecolor="rgba(0,0,0,0)"),
            yaxis=dict(showgrid=True, gridcolor=_LINE, zeroline=False, tickcolor="rgba(0,0,0,0)", linecolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.html("</div></div>")

    with col_right:
        seg_counts = filtered["seg_display"].value_counts().reset_index()
        seg_counts.columns = ["Segment", "Customers"]

        st.html("""
        <div class="obi-panel">
          <div class="obi-panel-head">
            <div>
              <div class="ptitle">Distribution</div>
              <h3>Segments by customer count</h3>
              <p>Breakdown of the customer base by RFM segment.</p>
            </div>
          </div>
          <div class="obi-panel-body">
        """)

        fig2 = go.Figure(go.Pie(
            labels=seg_counts["Segment"],
            values=seg_counts["Customers"],
            hole=0.6,
            marker=dict(colors=[color_map.get(s, "#CCC") for s in seg_counts["Segment"]]),
            textinfo="none",
            hovertemplate="%{label}<br>%{value:,} customers (%{percent})<extra></extra>",
        ))
        fig2.update_layout(
            height=280,
            margin=dict(t=0, r=0, l=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            font=dict(family="Manrope, sans-serif", size=11),
            annotations=[dict(
                text=f"<b style='font-size:24px'>{total:,}</b><br><span style='font-size:10px;color:{_MUTED}'>CUSTOMERS</span>",
                showarrow=False, font=dict(family="Instrument Serif, Georgia, serif", size=24, color="#11161E"),
            )],
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

        # Legend grid
        legend_items = ""
        for _, row in seg_counts.iterrows():
            pct = row["Customers"] / total * 100 if total else 0
            col = color_map.get(row["Segment"], "#CCC")
            legend_items += f"""
            <div style="display:flex;align-items:center;gap:8px;font-size:12px;padding:4px 0">
              <span style="width:9px;height:9px;border-radius:2px;background:{col};flex-shrink:0"></span>
              <span style="flex:1;color:var(--ink-2)">{row['Segment']}</span>
              <span style="font-family:var(--f-mono);font-size:11.5px;color:var(--muted)">{pct:.1f}%</span>
            </div>"""
        st.html(f"""
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px 12px;margin-top:8px">{legend_items}</div>
          </div></div>
        """)

    # ── Segment summary table ────────────────────────────────────────────────────
    summary = (
        filtered.groupby("seg_display")
        .agg(
            Customers=("customer_unique_id", "count"),
            Avg_AOV=("monetary_value", "mean"),
            Avg_Recency=("recency_days", "mean"),
            Avg_Frequency=("frequency_orders", "mean"),
        ).reset_index().sort_values("Customers", ascending=False)
    )

    rows_html = ""
    for _, row in summary.iterrows():
        col = color_map.get(row["seg_display"], "#CCC")
        share = row["Customers"] / total * 100 if total else 0
        rows_html += f"""
        <tr>
          <td><span style="width:10px;height:10px;border-radius:2px;background:{col};display:inline-block"></span></td>
          <td style="font-weight:600;color:var(--ink)">{row['seg_display']}</td>
          <td class="num">{int(row['Customers']):,}</td>
          <td class="num">R$ {row['Avg_AOV']:,.0f}</td>
          <td class="num">{row['Avg_Recency']:.0f}d</td>
          <td class="num">{row['Avg_Frequency']:.1f}</td>
          <td>
            <div style="display:flex;align-items:center;gap:8px">
              <div class="obi-bar-track" style="flex:1">
                <div class="obi-bar-fill" style="width:{share:.1f}%;background:{col}"></div>
              </div>
              <span style="font-family:var(--f-mono);font-size:12px;min-width:40px;text-align:right">{share:.1f}%</span>
            </div>
          </td>
        </tr>"""

    st.html(f"""
    <div class="obi-panel" style="margin-top:14px">
      <div class="obi-panel-head">
        <div>
          <div class="ptitle">Detail</div>
          <h3>Segment summary</h3>
          <p>One row per segment. Bars are scaled within column.</p>
        </div>
      </div>
      <div class="obi-panel-body" style="padding:0">
        <table class="obi-table">
          <thead>
            <tr>
              <th style="width:28px"></th>
              <th>Segment</th>
              <th class="num">Customers</th>
              <th class="num">Avg spend</th>
              <th class="num">Avg recency</th>
              <th class="num">Avg frequency</th>
              <th style="min-width:180px">Share</th>
            </tr>
          </thead>
          <tbody>{rows_html}</tbody>
        </table>
      </div>
    </div>
    """)
