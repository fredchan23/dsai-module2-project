import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Olist BI Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design system CSS ──────────────────────────────────────────────────────────
st.html("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif&family=JetBrains+Mono:wght@400;500&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
/* ── Tokens ─────────────────────────────────────────────────────────────────── */
:root {
  --bg:         #F4F2EC;
  --bg-elev:    #FBFAF6;
  --card:       #FFFFFF;
  --ink:        #11161E;
  --ink-2:      #2A323D;
  --muted:      #6B7480;
  --muted-2:    #9AA1AB;
  --line:       #E6E1D4;
  --line-strong:#D6CFBD;
  --side:       #0E1620;
  --side-2:     #15202D;
  --side-line:  #1F2B3A;
  --side-ink:   #E9EBEF;
  --side-muted: #8893A2;
  --accent:     #C47149;
  --accent-ink: #6B3420;
  --accent-soft:#F5EDE6;
  --pos:        #4A8E6C;
  --pos-soft:   #E6F4ED;
  --neg:        #A33028;
  --neg-soft:   #F6EAE8;
  --warn:       #C89030;
  --warn-soft:  #F5EDD6;
  --f-ui:       'Manrope', system-ui, sans-serif;
  --f-display:  'Instrument Serif', Georgia, serif;
  --f-mono:     'JetBrains Mono', ui-monospace, monospace;
}

/* ── Global ─────────────────────────────────────────────────────────────────── */
html, body, [data-testid="stApp"] {
  font-family: var(--f-ui) !important;
  background: var(--bg) !important;
  color: var(--ink) !important;
}
.main .block-container {
  padding: 1.5rem 2rem 4rem !important;
  max-width: 100% !important;
}

/* ── Sidebar ─────────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] > div:first-child {
  background: var(--side) !important;
  border-right: 1px solid var(--side-line) !important;
}
[data-testid="stSidebar"] * {
  color: var(--side-ink) !important;
  font-family: var(--f-ui) !important;
}
[data-testid="stSidebar"] hr {
  border-color: var(--side-line) !important;
  opacity: 1 !important;
  margin: 0.6rem 0 !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdown"] p,
[data-testid="stSidebar"] [data-testid="stMarkdown"] span {
  color: var(--side-muted) !important;
  font-size: 11.5px !important;
}
[data-testid="stSidebarHeader"] { display: none !important; }
/* radio nav */
[data-testid="stSidebar"] [role="radiogroup"] { gap: 2px !important; }
[data-testid="stSidebar"] label[data-baseweb="radio"] {
  padding: 8px 10px !important;
  border-radius: 6px !important;
  border: 1px solid transparent !important;
  transition: background 120ms ease !important;
  font-size: 13.5px !important;
  font-family: var(--f-ui) !important;
  color: var(--side-ink) !important;
}
[data-testid="stSidebar"] label[data-baseweb="radio"]:hover {
  background: var(--side-2) !important;
}
[data-testid="stSidebar"] label[data-baseweb="radio"][aria-checked="true"] {
  background: var(--side-2) !important;
  border-color: var(--side-line) !important;
  color: var(--accent) !important;
}
[data-testid="stSidebar"] label[data-baseweb="radio"][aria-checked="true"] p {
  color: var(--accent) !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] > label { display: none !important; }

/* ── KPI cards ───────────────────────────────────────────────────────────────── */
.obi-kpis { display: grid; gap: 14px; margin-bottom: 24px; }
.obi-kpis.four  { grid-template-columns: repeat(4, 1fr); }
.obi-kpis.three { grid-template-columns: repeat(3, 1fr); }
.obi-kpi {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 18px 20px 20px;
  position: relative;
  overflow: hidden;
  font-family: var(--f-ui);
}
.obi-kpi .kpi-label {
  display: flex; align-items: center; gap: 7px;
  font-size: 11px; letter-spacing: .12em; text-transform: uppercase;
  color: var(--muted); font-weight: 600;
}
.obi-kpi .kpi-ico {
  width: 18px; height: 18px;
  display: grid; place-items: center;
  background: var(--accent-soft); border-radius: 5px;
  font-size: 10px; color: var(--accent-ink);
}
.obi-kpi .kpi-value {
  font-family: var(--f-display);
  font-size: 44px; line-height: 1.05; letter-spacing: -.02em;
  margin-top: 10px; color: var(--ink);
  display: flex; align-items: baseline; gap: 6px;
}
.obi-kpi .kpi-pre  { font-family: var(--f-ui); font-size: 16px; color: var(--muted-2); font-weight: 500; align-self: center; margin-right: 2px; }
.obi-kpi .kpi-unit { font-family: var(--f-ui); font-size: 14px; color: var(--muted); font-weight: 500; }
.obi-kpi .kpi-delta {
  display: inline-flex; align-items: center; gap: 4px;
  font-family: var(--f-mono); font-size: 11px;
  color: var(--pos); margin-top: 10px;
  padding: 3px 7px; background: var(--pos-soft); border-radius: 999px;
}
.obi-kpi .kpi-delta.neg { color: var(--neg); background: var(--neg-soft); }

/* ── Panels ──────────────────────────────────────────────────────────────────── */
.obi-panel {
  background: var(--card); border: 1px solid var(--line);
  border-radius: 10px; overflow: hidden; margin-bottom: 14px;
}
.obi-panel-head {
  display: flex; align-items: flex-start; justify-content: space-between;
  gap: 16px; padding: 18px 20px 12px;
  border-bottom: 1px solid var(--line);
}
.obi-panel-head .ptitle {
  font-size: 11px; letter-spacing: .14em; text-transform: uppercase;
  color: var(--muted); font-weight: 600; margin-bottom: 4px;
}
.obi-panel-head h3 {
  margin: 0 0 2px; font-family: var(--f-display); font-weight: 400;
  font-size: 22px; line-height: 1.1; letter-spacing: -.01em; color: var(--ink);
}
.obi-panel-head p { margin: 0; font-size: 12px; color: var(--muted); max-width: 56ch; }
.obi-panel-body  { padding: 16px 20px 20px; }
.obi-panel-foot {
  border-top: 1px solid var(--line); padding: 10px 20px;
  display: flex; justify-content: space-between;
  font-size: 12px; color: var(--muted); background: var(--bg-elev);
}

/* ── Page header ─────────────────────────────────────────────────────────────── */
.obi-page-head {
  display: flex; align-items: flex-end; justify-content: space-between;
  margin-bottom: 24px; gap: 24px;
}
.obi-eyebrow {
  font-size: 11px; letter-spacing: .18em; text-transform: uppercase;
  color: var(--muted); font-weight: 600; margin-bottom: 8px;
}
.obi-page-head h1 {
  font-family: var(--f-display); font-weight: 400; font-size: 42px;
  line-height: 1; letter-spacing: -.02em; margin: 0 0 8px; color: var(--ink);
}
.obi-page-head .sub { margin: 0; color: var(--muted); font-size: 13.5px; max-width: 56ch; }
.obi-meta { display: flex; gap: 12px; align-items: center; white-space: nowrap; }
.obi-pill {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 5px 9px; border: 1px solid var(--line);
  border-radius: 999px; background: var(--bg-elev);
  color: var(--ink-2); font-size: 12px;
}

/* ── Section divider ─────────────────────────────────────────────────────────── */
.obi-section-title {
  font-size: 11px; letter-spacing: .16em; text-transform: uppercase;
  color: var(--muted); font-weight: 600; margin: 28px 0 12px;
  display: flex; align-items: center; gap: 12px;
}
.obi-section-title::after { content:''; flex:1; height:1px; background: var(--line); }

/* ── Grid ────────────────────────────────────────────────────────────────────── */
.obi-grid { display: grid; gap: 14px; }
.obi-grid.cols-2  { grid-template-columns: 1.4fr 1fr; }
.obi-grid.cols-2e { grid-template-columns: 1fr 1fr; }
.obi-grid.cols-3  { grid-template-columns: repeat(3, 1fr); }

/* ── Tables ──────────────────────────────────────────────────────────────────── */
.obi-table { width: 100%; border-collapse: collapse; font-size: 13px; font-family: var(--f-ui); }
.obi-table th {
  text-align: left; font-weight: 600; font-size: 10px; letter-spacing: .12em;
  text-transform: uppercase; color: var(--muted); padding: 10px 14px;
  background: var(--bg-elev); border-bottom: 1px solid var(--line); white-space: nowrap;
}
.obi-table th.num, .obi-table td.num {
  text-align: right; font-family: var(--f-mono); font-size: 12px;
}
.obi-table td {
  padding: 10px 14px; border-bottom: 1px solid var(--line);
  color: var(--ink-2); vertical-align: middle;
}
.obi-table tr:last-child td { border-bottom: 0; }
.obi-table tr:hover td { background: var(--bg-elev); }

/* ── Mini components ─────────────────────────────────────────────────────────── */
.obi-rank {
  display: inline-grid; place-items: center;
  width: 22px; height: 22px; font-family: var(--f-mono); font-size: 10px;
  background: var(--bg); color: var(--muted); border-radius: 5px;
  border: 1px solid var(--line);
}
.obi-rank.top { background: var(--accent-soft); color: var(--accent-ink); border-color: transparent; }
.obi-chip {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 2px 7px; border-radius: 999px;
  background: var(--bg); border: 1px solid var(--line);
  font-size: 11px; color: var(--ink-2); font-weight: 500;
}
.obi-chip.pos { background: var(--pos-soft); border-color: transparent; color: var(--pos); }
.obi-chip.neg { background: var(--neg-soft); border-color: transparent; color: var(--neg); }
.obi-chip.warn { background: var(--warn-soft); border-color: transparent; color: var(--warn); }
.obi-mono { font-family: var(--f-mono); font-size: 12px; color: var(--muted); }
.obi-bar-track {
  height: 6px; background: var(--bg); border-radius: 3px; overflow: hidden; flex: 1;
}
.obi-bar-fill { height: 100%; border-radius: 3px; }

/* ── Note card ───────────────────────────────────────────────────────────────── */
.obi-note {
  border-left: 2px solid var(--accent); background: var(--accent-soft);
  padding: 10px 14px; border-radius: 0 6px 6px 0;
  font-size: 12.5px; color: var(--accent-ink); margin-top: 16px;
}

/* ── Mini stat ───────────────────────────────────────────────────────────────── */
.obi-mini-stat {
  display: flex; justify-content: space-between; align-items: baseline;
  padding: 10px 0; border-bottom: 1px solid var(--line);
}
.obi-mini-stat .ms-label { font-size: 12.5px; color: var(--muted); }
.obi-mini-stat .ms-value { font-family: var(--f-mono); font-size: 13px; color: var(--ink); font-weight: 500; }

/* ── Composition bar ─────────────────────────────────────────────────────────── */
.obi-comp-bar { display: flex; height: 24px; border-radius: 4px; overflow: hidden; margin-bottom: 12px; }

/* ── Topbar ──────────────────────────────────────────────────────────────────── */
.obi-topbar {
  position: sticky; top: 0; z-index: 10;
  background: rgba(244,242,236,0.85);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--line);
  padding: 13px 32px;
  margin: -1.5rem -2rem 1.5rem;
  display: flex; align-items: center;
}
.obi-crumb {
  font-size: 12px; color: var(--muted); letter-spacing: .02em;
}
.obi-crumb b { color: var(--ink); font-weight: 600; }
.obi-crumb-sep { margin: 0 7px; color: var(--muted-2); }

/* ── Selectbox overrides ─────────────────────────────────────────────────────── */
[data-testid="stSelectbox"] label {
  font-size: 11px !important; letter-spacing: .1em !important;
  text-transform: uppercase !important; font-weight: 600 !important;
  color: var(--muted) !important; font-family: var(--f-ui) !important;
}
[data-testid="stSelectbox"] > div > div[data-baseweb="select"] > div {
  background: var(--card) !important;
  border: 1px solid var(--line-strong) !important;
  border-radius: 8px !important;
}
[data-testid="stSelectbox"] > div > div[data-baseweb="select"] > div:hover {
  border-color: var(--accent) !important;
}
[data-testid="stSelectbox"] span {
  color: var(--ink) !important;
  font-family: var(--f-ui) !important;
  font-size: 13px !important;
}

/* ── Streamlit overrides ─────────────────────────────────────────────────────── */
[data-testid="stHorizontalBlock"] { gap: 14px !important; }
[data-testid="stToolbar"] { display: none !important; }
.appview-container .main .block-container { padding-top: 1.5rem !important; }

/* ── Sidebar collapse button — always visible, styled to match dark sidebar ── */
[data-testid="collapsedControl"] {
  background: var(--side) !important;
  border-right: 1px solid var(--side-line) !important;
  color: var(--side-ink) !important;
}
[data-testid="collapsedControl"] svg { stroke: var(--side-ink) !important; }

/* ── Mobile: stack to full-width below 768px ─────────────────────────────────── */
@media (max-width: 768px) {
  [data-testid="stSidebar"] {
    width: 100% !important;
    min-width: unset !important;
  }
  [data-testid="stSidebar"] > div:first-child {
    height: auto !important;
    position: relative !important;
  }
  .main .block-container {
    padding: 1rem !important;
  }
  .obi-kpis.four  { grid-template-columns: repeat(2, 1fr) !important; }
  .obi-kpis.three { grid-template-columns: repeat(2, 1fr) !important; }
  .obi-grid.cols-2,
  .obi-grid.cols-2e,
  .obi-grid.cols-3  { grid-template-columns: 1fr !important; }
}
@media (max-width: 480px) {
  .obi-kpis.four,
  .obi-kpis.three { grid-template-columns: 1fr !important; }
  .obi-page-head  { flex-direction: column !important; align-items: flex-start !important; }
}
</style>
""")

# ── Sidebar ────────────────────────────────────────────────────────────────────
SECTIONS = {
    "Business Overview":  "overview",
    "Sales & Growth":     "sales",
    "Customer Health":    "customers",
    "Seller & Delivery":  "sellers",
}

with st.sidebar:
    st.html("""
    <div style="padding:20px 22px 16px;border-bottom:1px solid var(--side-line)">
      <div style="display:flex;align-items:center;gap:10px">
        <div style="width:30px;height:30px;background:var(--accent);border-radius:7px;display:grid;place-items:center;font-family:var(--f-display);font-size:20px;color:#fff;line-height:1">O</div>
        <div>
          <div style="font-weight:700;font-size:15px;letter-spacing:-.01em;color:var(--side-ink)">Olist BI</div>
          <div style="font-size:10.5px;color:var(--side-muted);letter-spacing:.06em;text-transform:uppercase;margin-top:1px">E-Commerce Analytics</div>
        </div>
      </div>
    </div>
    """)

    selection = st.radio(
        "Navigate to",
        list(SECTIONS.keys()),
        label_visibility="collapsed",
    )


    try:
        import db
        monthly = db.load_monthly_sales()
        max_month = monthly["month_start_date"].max() if len(monthly) else "—"
        freshness = str(max_month)[:10]
        pipeline = "Healthy"
    except Exception:
        freshness = "—"
        pipeline = "Connecting…"

    st.html(f"""
    <div style="margin-top:auto;padding:16px 22px 22px;border-top:1px solid var(--side-line);font-size:12px;color:var(--side-muted);line-height:1.7;margin-top:32px">
      <div style="display:flex;justify-content:space-between"><span>Data freshness</span><b style="color:var(--side-ink);font-family:var(--f-mono);font-size:11px">{freshness}</b></div>
      <div style="display:flex;justify-content:space-between;margin-top:4px"><span><span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--pos);margin-right:5px;vertical-align:middle"></span>Pipeline</span><b style="color:var(--side-ink);font-family:var(--f-mono);font-size:11px">{pipeline}</b></div>
      <div style="display:flex;justify-content:space-between;margin-top:4px"><span>Source</span><b style="color:var(--side-ink);font-family:var(--f-mono);font-size:11px">Snowflake · dbt</b></div>
    </div>
    """)

# ── Topbar ─────────────────────────────────────────────────────────────────────
section_key = SECTIONS[selection]

st.html(f"""
<div class="obi-topbar">
  <span class="obi-crumb">Workspace <span class="obi-crumb-sep">/</span> <b>{selection}</b></span>
</div>
""")

# ── Route ──────────────────────────────────────────────────────────────────────
if section_key == "overview":
    from sections.overview import render
elif section_key == "sales":
    from sections.sales import render
elif section_key == "customers":
    from sections.customers import render
else:
    from sections.sellers import render

render()
