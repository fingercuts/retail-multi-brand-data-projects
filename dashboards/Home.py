import streamlit as st
import os
from utils_dashboard import inject_premium_css, check_db_state, render_pbi_footer, load_data, format_currency, PBI_COLORS, get_sidebar_filters, render_premium_header

# --- PAGE SETUP ---
st.set_page_config(
    page_title="OmniRetail Analytics",
    page_icon="⬡",
    layout="wide",
)
inject_premium_css()
get_sidebar_filters()

# --- HEADER SECTION ---
render_premium_header("OmniRetail Holdings", "Enterprise Multi-Brand Analytics Platform")


# --- KPI STRIP ---
if check_db_state():
    kpi_data = load_data("""
        SELECT 
            COUNT(DISTINCT transaction_id) as transactions,
            SUM(net_amount) as revenue,
            COUNT(DISTINCT customer_id) as customers,
            COUNT(DISTINCT product_id) as products
        FROM fct_sales
    """)
    
    if not kpi_data.empty and kpi_data['revenue'][0] is not None:
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Revenue", format_currency(kpi_data['revenue'][0]))
        k2.metric("Transactions", f"{int(kpi_data['transactions'][0]):,d}")
        k3.metric("Customers", f"{int(kpi_data['customers'][0]):,d}")
        k4.metric("Products", f"{int(kpi_data['products'][0]):,d}")

    st.markdown("")

    # --- STATUS ROW ---
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown("""
            <div class="pbi-status-connected">
                <span class="pbi-status-dot"></span>
                Database Connected
            </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown("""
            <div class="pbi-status-connected">
                <span class="pbi-status-dot"></span>
                Marts Available
            </div>
        """, unsafe_allow_html=True)
    with s3:
        st.markdown("""
            <div class="pbi-status-connected" style="background:rgba(242,200,17,0.12); color:#F2C811;">
                <span class="pbi-status-dot" style="background:#F2C811;"></span>
                Live Refresh
            </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # --- MODULE CARDS ---
    st.markdown('<div class="pbi-section-title">Analytics Modules</div>', unsafe_allow_html=True)
    st.markdown("")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
            <div class="pbi-module-card">
                <div>
                    <div class="pbi-module-icon">📊</div>
                    <div class="pbi-module-title">Executive Overview</div>
                    <div class="pbi-module-desc">Corporate KPIs, revenue velocity, and brand portfolio performance at a glance.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
            <div class="pbi-module-card">
                <div>
                    <div class="pbi-module-icon">🏢</div>
                    <div class="pbi-module-title">Business Operations</div>
                    <div class="pbi-module-desc">Channel mix, regional revenue distribution, and store-level leaderboards.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
            <div class="pbi-module-card">
                <div>
                    <div class="pbi-module-icon">🛍️</div>
                    <div class="pbi-module-title">Product Insights</div>
                    <div class="pbi-module-desc">Category trends, SKU performance, price-volume correlation, and inventory health.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("")
    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown("""
            <div class="pbi-module-card">
                <div>
                    <div class="pbi-module-icon">👥</div>
                    <div class="pbi-module-title">Customer Analytics</div>
                    <div class="pbi-module-desc">Demographic segmentation, geographic distribution, and VIP customer profiling.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with c5:
        st.markdown("""
            <div class="pbi-module-card">
                <div>
                    <div class="pbi-module-icon">🎯</div>
                    <div class="pbi-module-title">Promotion Analysis</div>
                    <div class="pbi-module-desc">Campaign effectiveness, discount impact, and promotional ROI tracking.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with c6:
        st.markdown("""
            <div class="pbi-module-card" style="border-style:dashed; opacity:0.5;">
                <div>
                    <div class="pbi-module-icon">🔮</div>
                    <div class="pbi-module-title">Predictive (Coming Soon)</div>
                    <div class="pbi-module-desc">ML-powered demand forecasting, churn prediction, and basket analysis.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # --- ARCHITECTURE SECTION ---
    st.markdown('<div class="pbi-section-title">Data Architecture</div>', unsafe_allow_html=True)
    st.markdown("")

    a1, a2, a3, a4 = st.columns(4)
    layers = [
        ("a1", "🔵", "Raw", "Source CSV extracts from brand-level ERPs"),
        ("a2", "🟡", "Staging", "Standardized Parquet with cleansing & PII masking"),
        ("a3", "🟢", "Marts", "Star schema models built in dbt"),
        ("a4", "🟣", "Serving", "Interactive dashboard & REST API"),
    ]
    for col, icon, name, desc in zip([a1, a2, a3, a4], *zip(*[(l[1], l[2], l[3]) for l in layers])):
        with col:
            st.markdown(f"""
                <div style="background:#252525; border:1px solid #333; border-radius:8px; padding:24px 16px; text-align:center; height:180px; display:flex; flex-direction:column; justify-content:flex-start; align-items:center;">
                    <div style="font-size:1.5rem; margin-bottom:12px;">{icon}</div>
                    <div style="color:#FFF; font-weight:600; font-size:0.9rem; margin-bottom:8px;">{name}</div>
                    <div style="color:#888; font-size:0.72rem; line-height:1.4;">{desc}</div>
                </div>
            """, unsafe_allow_html=True)

else:
    st.error("⚠️ Analytical database not connected. Please run the ingestion and dbt-build pipelines.")

# --- FOOTER ---
render_pbi_footer()
