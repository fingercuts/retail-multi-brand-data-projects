import streamlit as st
import plotly.express as px
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils_dashboard import load_data, inject_premium_css, check_db_state, get_sidebar_filters

# --- PAGE SETUP ---
st.set_page_config(page_title="Business Operations | Retail Insights Pro", layout="wide")
inject_premium_css()

if check_db_state():
    # --- HEADER ---
    st.markdown('<h1 class="main-header">Business Operations</h1>', unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 1.2rem;'>Regional Performance, Channel Mix & Store Strategy</p>", unsafe_allow_html=True)
    
    # --- FILTERS ---
    filter_sql = get_sidebar_filters()

    # --- CHARTS SECTION 1: CHANNEL & REGION ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("### 🌍 Channel Performance Mix")
        channel_data = load_data(f"""
            SELECT 
                COALESCE(ch.channel_name, CASE WHEN s.channel_id IS NOT NULL THEN 'Digital/Unmapped' ELSE 'Direct Offline' END) as channel,
                SUM(net_amount) as revenue
            FROM fct_sales s
            JOIN dim_products p ON s.product_id = p.product_id
            LEFT JOIN dim_stores st ON s.store_id = st.store_id
            LEFT JOIN dim_channels ch ON s.channel_id = ch.channel_id
            {filter_sql}
            GROUP BY 1 ORDER BY 2 DESC
        """)
        if not channel_data.empty:
            fig_chan = px.sunburst(channel_data, path=['channel'], values='revenue',
                                 color='revenue', color_continuous_scale='Turbo')
            fig_chan.update_layout(height=450, margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_chan, use_container_width=True)
        else:
            st.info("No channel data.")

    with c2:
        st.markdown("### 🗺️ Revenue by Region")
        region_data = load_data(f"""
            SELECT st.region, SUM(net_amount) as revenue
            FROM fct_sales s
            LEFT JOIN dim_stores st ON s.store_id = st.store_id
            JOIN dim_products p ON s.product_id = p.product_id
            {filter_sql}
            GROUP BY 1 ORDER BY 2 DESC
        """)
        if not region_data.empty:
            fig_reg = px.bar(region_data, x='revenue', y='region', orientation='h',
                           color='revenue', color_continuous_scale='Blues')
            fig_reg.update_layout(height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
            st.plotly_chart(fig_reg, use_container_width=True)
        else:
            st.info("No regional data.")

    # --- STORE LEADERBOARD ---
    st.markdown("---")
    st.markdown("### 🏆 Top 15 Outlets by Revenue")
    store_leaderboard = load_data(f"""
        SELECT 
            st.store_name, 
            st.region, 
            COALESCE(ch.channel_name, 'Offline') as type, 
            SUM(net_amount) as revenue,
            COUNT(DISTINCT s.transaction_id) as transactions
        FROM fct_sales s
        LEFT JOIN dim_stores st ON s.store_id = st.store_id
        JOIN dim_products p ON s.product_id = p.product_id
        LEFT JOIN dim_channels ch ON s.channel_id = ch.channel_id
        {filter_sql}
        GROUP BY 1, 2, 3 ORDER BY 4 DESC LIMIT 15
    """)
    if not store_leaderboard.empty:
        st.dataframe(store_leaderboard.style.format({"revenue": "Rp {:.0f}", "transactions": "{:,d}"}), use_container_width=True)
    else:
        st.info("No store data.")
