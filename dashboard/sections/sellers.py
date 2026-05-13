import streamlit as st

import db

_ACCENT = "#C47149"
_POS    = "#4A8E6C"
_NEG    = "#A33028"
_WARN   = "#C89030"
_LINE   = "#E6E1D4"
_MUTED  = "#6B7480"


def _otr_color(rate: float) -> str:
    if rate >= 0.93:
        return _POS
    if rate >= 0.90:
        return "#6AA87A"
    if rate >= 0.87:
        return "#C8B060"
    return "#C47149"


def render():
    sellers_df  = db.load_seller_performance()
    delivery_df = db.load_delivery_performance()

    overall_otr = delivery_df["on_time_delivery_rate"].mean() * 100 if len(delivery_df) else 0
    avg_review  = sellers_df["average_review_score"].mean() if len(sellers_df) else 0
    pct_hi      = (sellers_df["average_review_score"] >= 4).sum() / len(sellers_df) * 100 if len(sellers_df) else 0

    st.html("""
    <div class="obi-page-head">
      <div>
        <div class="obi-eyebrow">Section 04 · Operations</div>
        <h1>Seller &amp; Delivery</h1>
        <p class="sub">Marketplace fulfillment quality, top revenue sellers, and regional on-time performance.</p>
      </div>
      <div class="obi-meta">
        <span class="obi-pill">{active} active sellers</span>
        <span class="obi-pill">{states} states</span>
      </div>
    </div>
    """.format(active=f"{len(sellers_df):,}", states=len(delivery_df)))

    # ── KPIs ─────────────────────────────────────────────────────────────────────
    st.html(f"""
    <div class="obi-kpis three">
      <div class="obi-kpi">
        <div class="kpi-label"><span class="kpi-ico">🚚</span>Overall On-Time Delivery</div>
        <div class="kpi-value">{overall_otr:.1f}<span class="kpi-unit">%</span></div>
        <div class="kpi-delta">▲ platform average</div>
      </div>
      <div class="obi-kpi">
        <div class="kpi-label"><span class="kpi-ico">★</span>Avg Seller Review</div>
        <div class="kpi-value">{avg_review:.2f}<span class="kpi-unit">/ 5.0</span></div>
        <div class="kpi-delta">▲ vs prior period</div>
      </div>
      <div class="obi-kpi">
        <div class="kpi-label"><span class="kpi-ico">✓</span>Sellers with Score ≥ 4</div>
        <div class="kpi-value">{pct_hi:.0f}<span class="kpi-unit">%</span></div>
        <div class="kpi-delta">▲ of active sellers</div>
      </div>
    </div>
    """)

    # ── Seller leaderboard ───────────────────────────────────────────────────────
    top10 = sellers_df.head(10).copy()

    rows_html = ""
    for i, (_, row) in enumerate(top10.iterrows()):
        rank_cls = "top" if i < 3 else ""
        sid = str(row["seller_id"])
        sid_short = sid[:12] + "…" + sid[-4:] if len(sid) > 16 else sid

        otr_val = row["on_time_delivery_rate"] * 100
        otr_color = _POS if otr_val >= 93 else (_ACCENT if otr_val >= 88 else _WARN)

        rev_score = row["average_review_score"]
        chip_cls = "pos" if rev_score >= 4.1 else ("neg" if rev_score < 3.9 else "")

        rows_html += f"""
        <tr>
          <td><span class="obi-rank {rank_cls}">{str(i+1).zfill(2)}</span></td>
          <td><span class="obi-mono">{sid_short}</span></td>
          <td><span class="obi-chip">{row['seller_state']}</span></td>
          <td class="num">{int(row['order_count']):,}</td>
          <td class="num">R$ {row['revenue_incl_freight']:,.0f}</td>
          <td>
            <div style="display:flex;align-items:center;gap:8px;min-width:160px">
              <div class="obi-bar-track" style="flex:1">
                <div class="obi-bar-fill" style="width:{otr_val:.1f}%;background:{otr_color}"></div>
              </div>
              <span style="font-family:var(--f-mono);font-size:12px;min-width:44px;text-align:right">{otr_val:.1f}%</span>
            </div>
          </td>
          <td class="num"><span class="obi-chip {chip_cls}">★ {rev_score:.2f}</span></td>
        </tr>"""

    st.html(f"""
    <div class="obi-panel">
      <div class="obi-panel-head">
        <div>
          <div class="ptitle">Leaderboard</div>
          <h3>Top sellers by revenue</h3>
          <p>The ten merchants powering the most marketplace revenue this period.</p>
        </div>
      </div>
      <div class="obi-panel-body" style="padding:0">
        <table class="obi-table">
          <thead>
            <tr>
              <th style="width:36px">#</th>
              <th>Seller ID</th>
              <th>State</th>
              <th class="num">Orders</th>
              <th class="num">Revenue</th>
              <th>On-time rate</th>
              <th class="num">Review</th>
            </tr>
          </thead>
          <tbody>{rows_html}</tbody>
        </table>
      </div>
      <div class="obi-panel-foot">
        <span>Showing 10 of {len(sellers_df):,} sellers</span>
        <span>Sorted by revenue · descending</span>
      </div>
    </div>
    """)

    # ── Geography + Watchlist ────────────────────────────────────────────────────
    col_left, col_right = st.columns([1, 1])

    delivery_sorted = delivery_df.sort_values("on_time_delivery_rate", ascending=False)

    with col_left:
        geo_rows = ""
        for _, row in delivery_sorted.iterrows():
            otr = row["on_time_delivery_rate"] * 100
            color = _otr_color(row["on_time_delivery_rate"])
            orders = int(row["order_count"]) if "order_count" in row else 0
            orders_fmt = f"{orders:,} ord." if orders else ""
            geo_rows += f"""
            <div style="display:grid;grid-template-columns:40px 1fr 70px 90px;gap:12px;align-items:center;margin-bottom:8px">
              <div style="font-family:var(--f-mono);font-size:12px;color:var(--ink-2);font-weight:600">{row['customer_state']}</div>
              <div style="height:14px;background:var(--bg);border-radius:4px;overflow:hidden">
                <div style="height:100%;width:{otr:.1f}%;background:{color};border-radius:4px"></div>
              </div>
              <div style="font-family:var(--f-mono);font-size:12px;text-align:right;color:var(--ink-2)">{otr:.1f}%</div>
              <div style="font-family:var(--f-mono);font-size:11px;text-align:right;color:var(--muted)">{orders_fmt}</div>
            </div>"""

        st.html(f"""
        <div class="obi-panel">
          <div class="obi-panel-head">
            <div>
              <div class="ptitle">Geography</div>
              <h3>On-time rate by state</h3>
              <p>Bars colored by performance band.</p>
            </div>
          </div>
          <div class="obi-panel-body">
            {geo_rows}
            <div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:14px;font-size:12px;color:var(--ink-2)">
              <span><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:{_POS};margin-right:5px"></span>≥ 93%</span>
              <span><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:#6AA87A;margin-right:5px"></span>90–93%</span>
              <span><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:#C8B060;margin-right:5px"></span>87–90%</span>
              <span><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:{_ACCENT};margin-right:5px"></span>&lt; 87%</span>
            </div>
          </div>
        </div>
        """)

    with col_right:
        # States below 89% threshold (use 0.89 on 0–1 scale)
        target = 0.89
        watchlist = delivery_sorted[delivery_sorted["on_time_delivery_rate"] < target].sort_values(
            "on_time_delivery_rate"
        )

        watch_items = ""
        for _, row in watchlist.iterrows():
            otr = row["on_time_delivery_rate"] * 100
            orders = int(row["order_count"]) if "order_count" in row else 0
            late = round(orders * (1 - row["on_time_delivery_rate"]))
            pp_below = 89 - otr
            chip_cls = "neg" if otr < 85 else "warn"
            watch_items += f"""
            <div style="display:grid;grid-template-columns:60px 1fr auto;gap:12px;align-items:center;
                        padding:12px 14px;border:1px solid var(--line);border-radius:8px;
                        background:var(--bg-elev);margin-bottom:10px">
              <div style="font-family:var(--f-display);font-size:28px;line-height:1;color:var(--ink)">{row['customer_state']}</div>
              <div>
                <div style="font-size:13px;color:var(--ink);font-weight:600">{otr:.1f}% on-time</div>
                <div style="font-size:12px;color:var(--muted);margin-top:2px">{late:,} late · {orders:,} total orders</div>
              </div>
              <span class="obi-chip {chip_cls}">{pp_below:.1f} pp below target</span>
            </div>"""

        if not watch_items:
            watch_items = '<p style="color:var(--muted);font-size:13px">All states are meeting the 89% target.</p>'

        st.html(f"""
        <div class="obi-panel">
          <div class="obi-panel-head">
            <div>
              <div class="ptitle">Watchlist</div>
              <h3>States needing attention</h3>
              <p>Below the 89% target. Prioritized by lateness × order volume.</p>
            </div>
          </div>
          <div class="obi-panel-body">
            {watch_items}
            <div class="obi-note">
              States below target may benefit from escalation to regional logistics partners.
            </div>
          </div>
        </div>
        """)
