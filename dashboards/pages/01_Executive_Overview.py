import streamlit as st
import plotly.express as px
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils_dashboard import PBI_PALETTE, render_premium_header, load_data, inject_premium_css, check_db_state, get_sidebar_filters, format_currency, format_number

# --- PAGE SETUP ---
st.set_page_config(page_title="Executive Overview | Retail Insights Pro", layout="wide")
inject_premium_css()

if check_db_state():
    # --- HEADER ---
    render_premium_header("Executive Overview", "Corporate Key Performance Indicators & Revenue Velocity")
    
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
        m1.metric("Gross Revenue", format_currency(metrics['gross_revenue'][0]))
        m2.metric("Net Revenue", format_currency(metrics['revenue'][0]))
        m3.metric("Discount Impact", f"{discount_impact:.1f}%")
        m4.metric("Total Volume", format_number(metrics['units'][0]))
        m5.metric("Avg Order Value", format_currency(metrics['aov'][0]))

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
            fig_trend = px.line(trend_data, x='day', y='revenue', color='brand_name',
                               line_shape='spline', color_discrete_sequence=PBI_PALETTE, labels={'brand_name': 'Brand', 'revenue': 'Revenue', 'category': 'Category', 'channel': 'Channel', 'region': 'Region', 'age_group': 'Age Group', 'customers': 'Customers', 'city': 'City', 'gender': 'Gender', 'promo_status': 'Promotion Status', 'discount_pct': 'Discount %', 'day': 'Date', 'price': 'Price', 'margin': 'Margin'})
            fig_trend.update_yaxes(ticksuffix="  ", title="", automargin=True, tickfont=dict(size=14))
            fig_trend.update_layout(font=dict(color="#1E293B", size=14), hovermode="x unified", plot_bgcolor='rgba(0,0,0,0)', 
                                   paper_bgcolor='rgba(0,0,0,0)', height=500, font_color="#94a3b8")
            with st.container(border=True):
                st.plotly_chart(fig_trend, use_container_width=True, theme=None)
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
            fig_brand = px.bar(brand_data, x='revenue', y='brand_name', orientation='h', text_auto='.2s', labels={'brand_name': 'Brand', 'revenue': 'Revenue', 'category': 'Category', 'channel': 'Channel', 'region': 'Region', 'age_group': 'Age Group', 'customers': 'Customers', 'city': 'City', 'gender': 'Gender', 'promo_status': 'Promotion Status', 'discount_pct': 'Discount %', 'day': 'Date', 'price': 'Price', 'margin': 'Margin'})
            fig_brand.update_traces(marker_color='#118DFF')
            fig_brand.update_yaxes(dtick=1, ticksuffix="  ", title="", automargin=True, tickfont=dict(size=14))
            fig_brand.update_layout(yaxis={'categoryorder':'total ascending'})
            fig_brand.update_yaxes(dtick=1, ticksuffix="  ", title="", automargin=True, tickfont=dict(size=14))
            fig_brand.update_layout(font=dict(color="#1E293B", size=14), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=max(450, len(brand_data) * 25))
            with st.container(border=True):
                st.plotly_chart(fig_brand, use_container_width=True, theme=None)
