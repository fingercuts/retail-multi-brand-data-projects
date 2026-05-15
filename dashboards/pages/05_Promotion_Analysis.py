import streamlit as st
import plotly.express as px
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils_dashboard import render_premium_header, load_data, inject_premium_css, check_db_state, get_sidebar_filters, format_currency, PBI_PALETTE, pbi_chart_layout, format_number

# --- PAGE SETUP ---
st.set_page_config(page_title="Promotion Analysis | Retail Insights Pro", layout="wide")
inject_premium_css()

if check_db_state():
    # --- HEADER ---
    render_premium_header("Promotion & Marketing", "Campaign Effectiveness & Discount Impact Analysis")
    
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
        m3.metric("Total Discounts", format_currency(promo_metrics['total_discounts'][0]))
        m4.metric("Net Margin", format_currency(promo_metrics['net_revenue'][0]))

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
                                  color_discrete_sequence=['#0078D4', '#E5E7EB'], labels={'brand_name': 'Brand', 'revenue': 'Revenue', 'category': 'Category', 'channel': 'Channel', 'region': 'Region', 'age_group': 'Age Group', 'customers': 'Customers', 'city': 'City', 'gender': 'Gender', 'promo_status': 'Promotion Status', 'discount_pct': 'Discount %', 'day': 'Date', 'price': 'Price', 'margin': 'Margin'})
                fig_split.update_yaxes(ticksuffix="  ", title="", automargin=True, tickfont=dict(size=14))
                fig_split.update_layout(font=dict(color="#1E293B", size=14), paper_bgcolor='rgba(0,0,0,0)')
                with st.container(border=True):
                    st.plotly_chart(fig_split, use_container_width=True, theme=None)

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
                               color='promo_status', color_discrete_sequence=['#0078D4', '#6B7280'], labels={'brand_name': 'Brand', 'revenue': 'Revenue', 'category': 'Category', 'channel': 'Channel', 'region': 'Region', 'age_group': 'Age Group', 'customers': 'Customers', 'city': 'City', 'gender': 'Gender', 'promo_status': 'Promotion Status', 'discount_pct': 'Discount %', 'day': 'Date', 'price': 'Price', 'margin': 'Margin'})
                fig_atv.update_yaxes(ticksuffix="  ", title="", automargin=True, tickfont=dict(size=14))
                fig_atv.update_layout(font=dict(color="#1E293B", size=14), paper_bgcolor='rgba(0,0,0,0)', bargap=0.2, plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
                with st.container(border=True):
                    st.plotly_chart(fig_atv, use_container_width=True, theme=None)

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
            display_promos = top_promos.rename(columns={
                'promotion_name': 'Promotion Name',
                'discount_pct': 'Discount %',
                'transactions': 'Transactions',
                'revenue': 'Revenue',
                'total_discount': 'Total Discount'
            })
            st.dataframe(display_promos.style.format({
                "Discount %": "{:.1f}%",
                "Transactions": "{:,d}",
                "Revenue": format_currency,
                "Total Discount": format_currency
            }), use_container_width=True)
        else:
            st.info("No promotion data available for the selected filters.")

        # --- DISCOUNT EFFECTIVENESS ---
        st.markdown("---")
        st.markdown("### 💰 Discount Level vs Revenue")
        
        # Determine currency rate
        currency = st.session_state.get('selected_currency', 'USD')
        rates = {"IDR": 1, "USD": 1/15500, "EUR": 1/16500}
        symbols = {"IDR": "Rp", "USD": "$", "EUR": "€"}
        curr_rate = rates.get(currency, 1)
        curr_sym = symbols.get(currency, "$")

        discount_analysis = load_data(f"""
            SELECT 
                pr.discount_pct,
                SUM(s.net_amount) * {curr_rate} as revenue,
                COUNT(DISTINCT s.transaction_id) as transactions,
                p.brand_name as brand
            FROM fct_sales s
            JOIN dim_promotions pr ON s.promotion_id = pr.promotion_id
            JOIN dim_products p ON s.product_id = p.product_id
            LEFT JOIN dim_stores st ON s.store_id = st.store_id
            {filter_sql}
            GROUP BY 1, 4
        """)
        
        if not discount_analysis.empty:
            fig_discount = px.scatter(
                discount_analysis, 
                x='discount_pct', 
                y='revenue', 
                size='transactions',
                color='brand', 
                color_discrete_sequence=PBI_PALETTE,
                labels={'discount_pct': 'Discount %', 'revenue': f'Revenue ({currency})', 'brand': 'Brand'},
                title=f"Revenue by Discount Level & Brand ({currency})"
            )
            
            fig_discount.update_layout(pbi_chart_layout(height=500))
            # Format Y-axis to be human readable
            fig_discount.update_yaxes(tickprefix=curr_sym, tickformat=".2s")

            fig_discount.update_yaxes(ticksuffix="  ", title="", automargin=True, tickfont=dict(size=14))
            fig_discount.update_layout(font=dict(color="#1E293B", size=14), paper_bgcolor='rgba(0,0,0,0)', bargap=0.2, plot_bgcolor='rgba(0,0,0,0)')
            with st.container(border=True):
                st.plotly_chart(fig_discount, use_container_width=True, theme=None)
