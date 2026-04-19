import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils_dashboard import load_data, inject_premium_css, check_db_state, get_sidebar_filters

# --- PAGE SETUP ---
st.set_page_config(page_title="Customer Analytics | Retail Insights Pro", layout="wide")
inject_premium_css()

if check_db_state():
    # --- HEADER ---
    st.markdown('<h1 class="main-header">Customer Analytics</h1>', unsafe_allow_html=True)
    st.markdown("<p style='color: #6B7280; font-size: 1.2rem;'>Demographics, Geography & Customer Lifetime Value</p>", unsafe_allow_html=True)
    
    # --- FILTERS ---
    filter_sql = get_sidebar_filters()

    # --- CUSTOMER METRICS ---
    customer_metrics = load_data(f"""
        SELECT 
            COUNT(DISTINCT c.customer_id) as total_customers,
            SUM(s.net_amount) / COUNT(DISTINCT c.customer_id) as revenue_per_customer,
            AVG(c.age) as avg_age
        FROM fct_sales s
        JOIN dim_customers c ON s.customer_id = c.customer_id
        JOIN dim_products p ON s.product_id = p.product_id
        LEFT JOIN dim_stores st ON s.store_id = st.store_id
        {filter_sql}
    """)

    if not customer_metrics.empty:
        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Customers", f"{int(customer_metrics['total_customers'][0]):,d}")
        m2.metric("Revenue per Customer", f"Rp {customer_metrics['revenue_per_customer'][0]:,.0f}")
        m3.metric("Average Age", f"{customer_metrics['avg_age'][0]:.1f} years")

        # --- DEMOGRAPHICS ---
        st.markdown("---")
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("### 👥 Age Distribution")
            age_data = load_data(f"""
                SELECT 
                    CASE 
                        WHEN c.age < 25 THEN '18-24'
                        WHEN c.age < 35 THEN '25-34'
                        WHEN c.age < 45 THEN '35-44'
                        WHEN c.age < 55 THEN '45-54'
                        ELSE '55+'
                    END as age_group,
                    COUNT(DISTINCT c.customer_id) as customers,
                    SUM(s.net_amount) as revenue
                FROM fct_sales s
                JOIN dim_customers c ON s.customer_id = c.customer_id
                JOIN dim_products p ON s.product_id = p.product_id
                LEFT JOIN dim_stores st ON s.store_id = st.store_id
                {filter_sql}
                GROUP BY 1 ORDER BY 1
            """)
            if not age_data.empty:
                fig_age = px.bar(age_data, x='age_group', y='revenue', 
                               color='customers', color_continuous_scale='Blues')
                fig_age.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_age, use_container_width=True)

        with c2:
            st.markdown("### ⚧️ Gender Split")
            gender_data = load_data(f"""
                SELECT c.gender, SUM(s.net_amount) as revenue
                FROM fct_sales s
                JOIN dim_customers c ON s.customer_id = c.customer_id
                JOIN dim_products p ON s.product_id = p.product_id
                LEFT JOIN dim_stores st ON s.store_id = st.store_id
                {filter_sql}
                GROUP BY 1
            """)
            if not gender_data.empty:
                fig_gender = px.pie(gender_data, values='revenue', names='gender', hole=0.4,
                                   color_discrete_sequence=['#0078D4', '#F59E0B'])
                fig_gender.update_layout(paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_gender, use_container_width=True)

        # --- GEOGRAPHIC ANALYSIS ---
        st.markdown("---")
        st.markdown("### 🗺️ Geographic Revenue Distribution")
        geo_data = load_data(f"""
            SELECT c.city, c.region, SUM(s.net_amount) as revenue, COUNT(DISTINCT c.customer_id) as customers
            FROM fct_sales s
            JOIN dim_customers c ON s.customer_id = c.customer_id
            JOIN dim_products p ON s.product_id = p.product_id
            LEFT JOIN dim_stores st ON s.store_id = st.store_id
            {filter_sql}
            GROUP BY 1, 2 ORDER BY 3 DESC LIMIT 15
        """)
        if not geo_data.empty:
            fig_geo = px.bar(geo_data, x='revenue', y='city', orientation='h',
                           color='region', color_discrete_sequence=px.colors.qualitative.Set2)
            fig_geo.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=500)
            st.plotly_chart(fig_geo, use_container_width=True)

        # --- VIP CUSTOMERS ---
        st.markdown("---")
        st.markdown("### 💎 VIP Customers (Top 10 by Revenue)")
        vip_data = load_data(f"""
            SELECT c.customer_id, c.city, c.age, c.gender, SUM(s.net_amount) as total_revenue
            FROM fct_sales s
            JOIN dim_customers c ON s.customer_id = c.customer_id
            JOIN dim_products p ON s.product_id = p.product_id
            LEFT JOIN dim_stores st ON s.store_id = st.store_id
            {filter_sql}
            GROUP BY 1, 2, 3, 4 ORDER BY 5 DESC LIMIT 10
        """)
        if not vip_data.empty:
            st.dataframe(vip_data.style.format({"total_revenue": "Rp {:.0f}"}), use_container_width=True)
