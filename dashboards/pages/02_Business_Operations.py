import streamlit as st
import plotly.express as px
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils_dashboard import PBI_PALETTE, render_premium_header, load_data, inject_premium_css, check_db_state, get_sidebar_filters, format_currency, format_number

# --- PAGE SETUP ---
st.set_page_config(page_title="Business Operations | Retail Insights Pro", layout="wide")
inject_premium_css()

if check_db_state():
    # --- HEADER ---
    render_premium_header("Business Operations", "Regional Performance & Operational Efficiency")
    
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
            fig_chan = px.sunburst(channel_data, path=['channel'], values='revenue', color_discrete_sequence=PBI_PALETTE)
            fig_chan.update_yaxes(ticksuffix="  ", title="", automargin=True, tickfont=dict(size=14))
            fig_chan.update_layout(font=dict(color="#1E293B", size=14), height=450, paper_bgcolor='rgba(0,0,0,0)')
            with st.container(border=True):
                st.plotly_chart(fig_chan, use_container_width=True, theme=None)
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
            fig_reg = px.bar(region_data, x='revenue', y='region', orientation='h', labels={'brand_name': 'Brand', 'revenue': 'Revenue', 'category': 'Category', 'channel': 'Channel', 'region': 'Region', 'age_group': 'Age Group', 'customers': 'Customers', 'city': 'City', 'gender': 'Gender', 'promo_status': 'Promotion Status', 'discount_pct': 'Discount %', 'day': 'Date', 'price': 'Price', 'margin': 'Margin'})
            fig_reg.update_traces(marker_color='#12B5CB')
            fig_reg.update_yaxes(dtick=1, ticksuffix="  ", title="", automargin=True, tickfont=dict(size=14))
            fig_reg.update_layout(yaxis={'categoryorder':'total ascending'})
            fig_reg.update_yaxes(dtick=1, ticksuffix="  ", title="", automargin=True, tickfont=dict(size=14))
            fig_reg.update_layout(font=dict(color="#1E293B", size=14), height=max(450, len(region_data) * 25), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
            with st.container(border=True):
                st.plotly_chart(fig_reg, use_container_width=True, theme=None)
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
        display_stores = store_leaderboard.rename(columns={'store_name': 'Store Name', 'region': 'Region', 'type': 'Type', 'revenue': 'Revenue', 'transactions': 'Transactions'})
        st.dataframe(display_stores.style.format({"Revenue": format_currency, "Transactions": "{:,d}"}), use_container_width=True)
    else:
        st.info("No store data.")
