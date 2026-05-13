import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Olist BI Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

SECTIONS = {
    "📊 Business Overview": "overview",
    "📈 Sales & Growth": "sales",
    "👥 Customer Health": "customers",
    "🚚 Seller & Delivery": "sellers",
}

with st.sidebar:
    st.title("📦 Olist BI")
    st.caption("Brazilian E-Commerce Analytics")
    st.markdown("---")

    selection = st.radio("Navigate to", list(SECTIONS.keys()), label_visibility="collapsed")

    st.markdown("---")

    try:
        import db
        monthly = db.load_monthly_sales()
        if len(monthly):
            max_month = monthly["month_start_date"].max()
            st.caption(f"Data as of: **{max_month}**")
    except Exception:
        st.caption("Data: connecting…")

section_key = SECTIONS[selection]

if section_key == "overview":
    from sections.overview import render
elif section_key == "sales":
    from sections.sales import render
elif section_key == "customers":
    from sections.customers import render
else:
    from sections.sellers import render

render()
