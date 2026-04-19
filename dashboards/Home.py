import streamlit as st
import os
from utils_dashboard import inject_premium_css, check_db_state

# --- PAGE SETUP ---
st.set_page_config(
    page_title="OmniRetail Analytics",
    page_icon="📊",
    layout="wide",
)
inject_premium_css()

# --- HEADER SECTION ---
st.markdown('<h1 class="main-header">OmniRetail Holdings</h1>', unsafe_allow_html=True)
st.markdown("<p style='color: #2ECC71; font-size: 1.2rem; font-weight: 600; letter-spacing: 0.5px;'>Enterprise Multi-Brand Analytics Platform</p>", unsafe_allow_html=True)

st.markdown("---")

# --- CORE LANDING CONTENT ---
col_main, col_stats = st.columns([2, 1])

with col_main:
    st.markdown("""
    ### Dashboard Overview
    This platform provides a consolidated analytical view across all OmniRetail subsidiary brands. It integrates multi-source retail data into a unified star schema for performance tracking and executive reporting.
    
    #### Data Architecture
    The underlying system utilizes a Medallion architecture:
    1.  **Raw**: Source CSV extracts from brand-level ERPs.
    2.  **Staging**: Standardized Parquet files with universal cleansing and PII masking.
    3.  **Marts**: Analytical models built in **dbt** for unified reporting.
    4.  **Serving**: This interactive interface and a parallel REST API.

    #### Navigation
    Use the **sidebar** to access specific analytical modules:
    - **Executive Overview**: Corporate revenue metrics and growth velocity.
    - **Business Operations**: Regional performance and store-level dynamics.
    - **Product Insights**: Category distribution and SKU performance.
    - **Customer Analytics**: Demographic and geographic segmentation.
    - **Promotion Analysis**: ROI tracking for seasonal and brand-specific campaigns.
    """)

with col_stats:
    st.markdown("### System Status")
    if check_db_state():
        st.success("Analytical Database: Connected")
        st.info("Pipeline State: Marts Available")
    else:
        st.error("Analytical Database: Disconnected")
        st.warning("Please execute the ingestion and dbt-build sequences to populate the dashboard stores.")

st.markdown("""
<style>
    .retail-card {
        background: linear-gradient(135deg, #1E1E1E 0%, #172a23 100%);
        padding: 20px;
        border-radius: 8px;
        border-top: 3px solid #2ECC71;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        color: #F5F5F5;
        transition: all 0.3s ease;
    }
    .retail-card:hover {
        transform: scale(1.01);
        box-shadow: 0 8px 15px rgba(46,204,113,0.2);
    }
</style>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("### Decision Support Modules")
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown('<div class="retail-card"><strong>Revenue Trends</strong><br><br>Analyze growth patterns and performance anomalies across digital and physical channels.</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="retail-card"><strong>Brand Performance</strong><br><br>Evaluate brand-level contributions to the corporate bottom line and category health.</div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="retail-card"><strong>Regional Insight</strong><br><br>Gis-mapping and regional segmentation to optimize logistics and territory management.</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.caption("OmniRetail Analytics Platform")
