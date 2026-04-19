import streamlit as st
import plotly.express as px
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils_dashboard import load_data, inject_premium_css, check_db_state, get_sidebar_filters

# --- PAGE SETUP ---
st.set_page_config(page_title="Promotion Analysis | Retail Insights Pro", layout="wide")
inject_premium_css()

if check_db_state():
    # --- HEADER ---
    st.markdown('<h1 class="main-header">Promotion Analysis</h1>', unsafe_allow_html=True)
    st.markdown("<p style='color: #6B7280; font-size: 1.2rem;'>Campaign Effectiveness & Discount Impact</p>", unsafe_allow_html=True)
    
    # --- FILTERS ---
    filter_sql = get_sidebar_filters()

    # --- PROMOTION METRICS ---
    promo_metrics = load_data(f"""
        SELECT 
            COUNT(DISTINCT CASE WHEN s.promotion_id IS NOT NULL THEN s.transaction_id END) as promo_transactions,
            COUNT(DISTINCT s.transaction_id) as total_transactions,
            SUM(s.discount_amount) as total_discounts,
            SUM(s.total_amount) as gross_revenue,
            SUM(s.net_amount) as net_revenue
        FROM fct_sales s
        JOIN dim_products p ON s.product_id = p.product_id
        LEFT JOIN dim_stores st ON s.store_id = st.store_id
        {filter_sql}
    """)

    if not promo_metrics.empty:
        redemption_rate = (promo_metrics['promo_transactions'][0] / promo_metrics['total_transactions'][0]) * 100
        discount_impact = (promo_metrics['total_discounts'][0] / promo_metrics['gross_revenue'][0]) * 100
        
        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Redemption Rate", f"{redemption_rate:.1f}%")
        m2.metric("Discount Impact", f"{discount_impact:.1f}%")
        m3.metric("Total Discounts", f"Rp {promo_metrics['total_discounts'][0]:,.0f}")
        m4.metric("Net Margin", f"Rp {promo_metrics['net_revenue'][0]:,.0f}")

        # --- PROMO VS NON-PROMO ---
        st.markdown("---")
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("### 🎯 Promo vs Non-Promo Revenue")
            promo_split = load_data(f"""
                SELECT 
                    CASE WHEN s.promotion_id IS NOT NULL THEN 'With Promotion' ELSE 'No Promotion' END as promo_status,
                    SUM(s.net_amount) as revenue
                FROM fct_sales s
                JOIN dim_products p ON s.product_id = p.product_id
                LEFT JOIN dim_stores st ON s.store_id = st.store_id
                {filter_sql}
                GROUP BY 1
            """)
            if not promo_split.empty:
                fig_split = px.pie(promo_split, values='revenue', names='promo_status', hole=0.5,
                                  color_discrete_sequence=['#0078D4', '#E5E7EB'])
                fig_split.update_layout(paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_split, use_container_width=True)

        with c2:
            st.markdown("### 📊 Average Transaction Value")
            atv_comparison = load_data(f"""
                SELECT 
                    CASE WHEN s.promotion_id IS NOT NULL THEN 'With Promotion' ELSE 'No Promotion' END as promo_status,
                    AVG(s.net_amount) as avg_transaction_value
                FROM fct_sales s
                JOIN dim_products p ON s.product_id = p.product_id
                LEFT JOIN dim_stores st ON s.store_id = st.store_id
                {filter_sql}
                GROUP BY 1
            """)
            if not atv_comparison.empty:
                fig_atv = px.bar(atv_comparison, x='promo_status', y='avg_transaction_value',
                               color='promo_status', color_discrete_sequence=['#0078D4', '#6B7280'])
                fig_atv.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
                st.plotly_chart(fig_atv, use_container_width=True)

        # --- TOP PROMOTIONS ---
        st.markdown("---")
        st.markdown("### 🏆 Top 10 Promotions by Revenue Impact")
        top_promos = load_data(f"""
            SELECT 
                pr.promotion_name,
                pr.discount_pct,
                COUNT(DISTINCT s.transaction_id) as transactions,
                SUM(s.net_amount) as revenue,
                SUM(s.discount_amount) as total_discount
            FROM fct_sales s
            JOIN dim_promotions pr ON s.promotion_id = pr.promotion_id
            JOIN dim_products p ON s.product_id = p.product_id
            LEFT JOIN dim_stores st ON s.store_id = st.store_id
            {filter_sql}
            GROUP BY 1, 2 ORDER BY 4 DESC LIMIT 10
        """)
        if not top_promos.empty:
            st.dataframe(top_promos.style.format({
                "discount_pct": "{:.1f}%",
                "transactions": "{:,d}",
                "revenue": "Rp {:.0f}",
                "total_discount": "Rp {:.0f}"
            }), use_container_width=True)
        else:
            st.info("No promotion data available for the selected filters.")

        # --- DISCOUNT EFFECTIVENESS ---
        st.markdown("---")
        st.markdown("### 💰 Discount Level vs Revenue")
        discount_analysis = load_data(f"""
            SELECT 
                CASE 
                    WHEN pr.discount_pct < 10 THEN '0-10%'
                    WHEN pr.discount_pct < 20 THEN '10-20%'
                    WHEN pr.discount_pct < 30 THEN '20-30%'
                    ELSE '30%+'
                END as discount_range,
                SUM(s.net_amount) as revenue,
                COUNT(DISTINCT s.transaction_id) as transactions
            FROM fct_sales s
            JOIN dim_promotions pr ON s.promotion_id = pr.promotion_id
            JOIN dim_products p ON s.product_id = p.product_id
            LEFT JOIN dim_stores st ON s.store_id = st.store_id
            {filter_sql}
            GROUP BY 1 ORDER BY 1
        """)
        if not discount_analysis.empty:
            fig_discount = px.scatter(discount_analysis, x='discount_range', y='revenue', size='transactions',
                                     color='revenue', color_continuous_scale='Blues')
            fig_discount.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_discount, use_container_width=True)
