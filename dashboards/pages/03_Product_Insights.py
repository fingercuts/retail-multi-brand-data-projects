import streamlit as st
import plotly.express as px
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils_dashboard import load_data, inject_premium_css, check_db_state, get_sidebar_filters

# --- PAGE SETUP ---
st.set_page_config(page_title="Product Insights | Retail Insights Pro", layout="wide")
inject_premium_css()

if check_db_state():
    # --- HEADER ---
    st.markdown('<h1 class="main-header">Product Insights</h1>', unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 1.2rem;'>Category Performance, Product Mix & Pricing Dynamics</p>", unsafe_allow_html=True)
    
    # --- FILTERS ---
    filter_sql = get_sidebar_filters()

    # --- CATEGORY ANALYSIS ---
    st.markdown("---")
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("### 📦 Revenue by Category")
        cat_data = load_data(f"""
            SELECT p.category, SUM(net_amount) as revenue
            FROM fct_sales s
            JOIN dim_products p ON s.product_id = p.product_id
            LEFT JOIN dim_stores st ON s.store_id = st.store_id
            {filter_sql}
            GROUP BY 1 ORDER BY 2 DESC
        """)
        if not cat_data.empty:
            fig_cat = px.bar(cat_data, x='revenue', y='category', orientation='h',
                            color='revenue', color_continuous_scale='Purples', text_auto='.2s')
            fig_cat.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("No category data.")

    with c2:
        st.markdown("### 📊 Category Portfolio Mix")
        if not cat_data.empty:
            fig_pie = px.pie(cat_data, values='revenue', names='category', hole=0.4,
                            color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_pie, use_container_width=True)

    # --- TOP PRODUCTS ---
    st.markdown("---")
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("### 🏆 Top 10 Products by Revenue")
        product_leaderboard = load_data(f"""
            SELECT p.product_name, p.category, SUM(net_amount) as revenue, SUM(units_sold) as units
            FROM fct_sales s
            JOIN dim_products p ON s.product_id = p.product_id
            LEFT JOIN dim_stores st ON s.store_id = st.store_id
            {filter_sql}
            GROUP BY 1, 2 ORDER BY 3 DESC LIMIT 10
        """)
        if not product_leaderboard.empty:
            # Format the dataframe for display
            formatted_df = product_leaderboard.copy()
            formatted_df['revenue'] = formatted_df['revenue'].apply(lambda x: f"Rp {x:,.0f}")
            st.dataframe(formatted_df, use_container_width=True)
        else:
            st.info("No product data.")

    with col_right:
        st.markdown("### 🏷️ Price vs. Volume Correlation")
        price_data = load_data(f"""
            SELECT p.product_name, AVG(s.unit_price) as avg_price, SUM(s.units_sold) as total_units, p.category
            FROM fct_sales s
            JOIN dim_products p ON s.product_id = p.product_id
            LEFT JOIN dim_stores st ON s.store_id = st.store_id
            {filter_sql}
            GROUP BY 1, 4 ORDER BY 3 DESC LIMIT 100
        """)
        if not price_data.empty:
            fig_scatter = px.scatter(price_data, x="avg_price", y="total_units", color="category",
                                    hover_name="product_name", size="total_units",
                                    log_x=True, size_max=40)
            fig_scatter.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#1F2937")
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("No pricing data.")

    # --- INVENTORY INSIGHTS ---
    st.markdown("---")
    st.markdown("### 📦 Inventory Health & Slow-Moving SKUs")
    
    inventory_data = load_data(f"""
        SELECT 
            p.product_name,
            p.category,
            i.stock_on_hand,
            i.reorder_level,
            COALESCE(SUM(s.units_sold), 0) as units_sold_30d,
            CASE 
                WHEN i.stock_on_hand < i.reorder_level THEN 'Reorder Needed'
                WHEN COALESCE(SUM(s.units_sold), 0) < 10 THEN 'Slow-Moving'
                ELSE 'Healthy'
            END as status
        FROM dim_inventory i
        JOIN dim_products p ON i.product_id = p.product_id
        LEFT JOIN fct_sales s ON i.product_id = s.product_id 
            AND s.date >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY 1, 2, 3, 4
        HAVING status != 'Healthy'
        ORDER BY 6, 5
        LIMIT 15
    """)
    
    if not inventory_data.empty:
        st.dataframe(inventory_data.style.format({
            "stock_on_hand": "{:.0f}",
            "reorder_level": "{:.0f}",
            "units_sold_30d": "{:.0f}"
        }), use_container_width=True)
    else:
        st.success("✅ All inventory levels are healthy!")
