import streamlit as st
import plotly.express as px
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils_dashboard import PBI_PALETTE, render_premium_header, load_data, inject_premium_css, check_db_state, get_sidebar_filters, format_currency, format_number

# --- PAGE SETUP ---
st.set_page_config(page_title="Product Insights | Retail Insights Pro", layout="wide")
inject_premium_css()

if check_db_state():
    # --- HEADER ---
    render_premium_header("Product & Inventory", "SKU Performance, Pricing Analysis & Inventory Health")
    
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
            fig_cat = px.bar(cat_data, x='revenue', y='category', orientation='h', text_auto='.2s', labels={'brand_name': 'Brand', 'revenue': 'Revenue', 'category': 'Category', 'channel': 'Channel', 'region': 'Region', 'age_group': 'Age Group', 'customers': 'Customers', 'city': 'City', 'gender': 'Gender', 'promo_status': 'Promotion Status', 'discount_pct': 'Discount %', 'day': 'Date', 'price': 'Price', 'margin': 'Margin'})
            fig_cat.update_traces(marker_color='#A855F7')
            fig_cat.update_yaxes(dtick=1, ticksuffix="  ", title="", automargin=True, tickfont=dict(size=14))
            fig_cat.update_layout(yaxis={'categoryorder':'total ascending'})
            fig_cat.update_yaxes(dtick=1, ticksuffix="  ", title="", automargin=True, tickfont=dict(size=14))
            fig_cat.update_layout(font=dict(color="#1E293B", size=14), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=max(450, len(cat_data) * 25))
            with st.container(border=True):
                st.plotly_chart(fig_cat, use_container_width=True, theme=None)
        else:
            st.info("No category data.")

    with c2:
        st.markdown("### 📊 Category Portfolio Mix")
        if not cat_data.empty:
            fig_pie = px.pie(cat_data, values='revenue', names='category', hole=0.4,
                            color_discrete_sequence=PBI_PALETTE, labels={'brand_name': 'Brand', 'revenue': 'Revenue', 'category': 'Category', 'channel': 'Channel', 'region': 'Region', 'age_group': 'Age Group', 'customers': 'Customers', 'city': 'City', 'gender': 'Gender', 'promo_status': 'Promotion Status', 'discount_pct': 'Discount %', 'day': 'Date', 'price': 'Price', 'margin': 'Margin'})
            fig_pie.update_yaxes(ticksuffix="  ", title="", automargin=True, tickfont=dict(size=14))
            fig_pie.update_layout(font=dict(color="#1E293B", size=14), paper_bgcolor='rgba(0,0,0,0)')
            with st.container(border=True):
                st.plotly_chart(fig_pie, use_container_width=True, theme=None)

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
            formatted_df['revenue'] = formatted_df['revenue'].apply(format_currency)
            formatted_df = formatted_df.rename(columns={'product_name': 'Product Name', 'category': 'Category', 'revenue': 'Revenue', 'units': 'Units Sold'})
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
                                    log_x=True, size_max=40, labels={'brand_name': 'Brand', 'revenue': 'Revenue', 'category': 'Category', 'channel': 'Channel', 'region': 'Region', 'age_group': 'Age Group', 'customers': 'Customers', 'city': 'City', 'gender': 'Gender', 'promo_status': 'Promotion Status', 'discount_pct': 'Discount %', 'day': 'Date', 'price': 'Price', 'margin': 'Margin'})
            fig_scatter.update_yaxes(ticksuffix="  ", title="", automargin=True, tickfont=dict(size=14))
            fig_scatter.update_layout(font=dict(color="#1E293B", size=14), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#1F2937")
            with st.container(border=True):
                st.plotly_chart(fig_scatter, use_container_width=True, theme=None)
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
        display_inventory = inventory_data.rename(columns={
            'product_name': 'Product Name', 'category': 'Category', 
            'stock_on_hand': 'Stock on Hand', 'reorder_level': 'Reorder Level', 
            'units_sold_30d': 'Units Sold 30d', 'status': 'Status'
        })
        st.dataframe(display_inventory.style.format({
            "Stock on Hand": "{:.0f}",
            "Reorder Level": "{:.0f}",
            "Units Sold 30d": "{:.0f}"
        }), use_container_width=True)
    else:
        st.success("✅ All inventory levels are healthy!")
