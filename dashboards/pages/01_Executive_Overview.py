import streamlit as st
import plotly.express as px
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils_dashboard import load_data, inject_premium_css, check_db_state, get_sidebar_filters

# --- PAGE SETUP ---
st.set_page_config(page_title="Executive Overview | Retail Insights Pro", layout="wide")
inject_premium_css()

if check_db_state():
    # --- HEADER ---
    st.markdown('<h1 class="main-header">Executive Overview</h1>', unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 1.2rem;'>Corporate Key Performance Indicators & Revenue Velocity</p>", unsafe_allow_html=True)
    
    # --- FILTERS ---
    filter_sql = get_sidebar_filters()

    # --- DATA FETCHING ---
    metrics_query = f"""
        SELECT 
            SUM(total_amount) as gross_revenue,
            SUM(net_amount) as revenue,
            SUM(discount_amount) as total_discounts,
            SUM(units_sold) as units,
            COUNT(DISTINCT s.transaction_id) as transactions,
            AVG(net_amount) as aov
        FROM fct_sales s
        JOIN dim_products p ON s.product_id = p.product_id
        LEFT JOIN dim_stores st ON s.store_id = st.store_id
        {filter_sql}
    """
    metrics = load_data(metrics_query)

    if metrics.empty or metrics['revenue'][0] is None:
        st.warning("📊 No data found for the selected filters.")
    else:
        discount_impact = (metrics['total_discounts'][0] / metrics['gross_revenue'][0]) * 100 if metrics['gross_revenue'][0] > 0 else 0
        
        # --- SCORECARDS ---
        st.markdown("---")
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Gross Revenue", f"Rp {metrics['gross_revenue'][0]:,.0f}")
        m2.metric("Net Revenue", f"Rp {metrics['revenue'][0]:,.0f}")
        m3.metric("Discount Impact", f"{discount_impact:.1f}%")
        m4.metric("Total Volume", f"{int(metrics['units'][0]):,d}")
        m5.metric("Avg Order Value", f"Rp {metrics['aov'][0]:,.0f}")

        # --- REVENUE VELOCITY ---
        st.markdown("---")
        st.markdown("### 📈 Tactical Revenue Velocity")
        trend_data = load_data(f"""
            SELECT CAST(s.date AS DATE) as day, p.brand_name, SUM(net_amount) as revenue
            FROM fct_sales s
            JOIN dim_products p ON s.product_id = p.product_id
            LEFT JOIN dim_stores st ON s.store_id = st.store_id
            {filter_sql}
            GROUP BY 1, 2 ORDER BY 1
        """)
        if not trend_data.empty:
            fig_trend = px.area(trend_data, x='day', y='revenue', color='brand_name',
                               line_shape='spline', color_discrete_sequence=px.colors.qualitative.Prism)
            fig_trend.update_layout(hovermode="x unified", plot_bgcolor='rgba(0,0,0,0)', 
                                   paper_bgcolor='rgba(0,0,0,0)', height=500, font_color="#94a3b8")
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No trend data available.")

        # --- BRAND PERFORMANCE ---
        st.markdown("---")
        st.markdown("### 🏷️ Performance by Brand Portfolio")
        brand_data = load_data(f"""
            SELECT p.brand_name, SUM(net_amount) as revenue, SUM(units_sold) as units
            FROM fct_sales s
            JOIN dim_products p ON s.product_id = p.product_id
            LEFT JOIN dim_stores st ON s.store_id = st.store_id
            {filter_sql}
            GROUP BY 1 ORDER BY 2 DESC
        """)
        if not brand_data.empty:
            fig_brand = px.bar(brand_data, x='brand_name', y='revenue', color='revenue',
                              color_continuous_scale='Turbo', text_auto='.2s')
            fig_brand.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_brand, use_container_width=True)
