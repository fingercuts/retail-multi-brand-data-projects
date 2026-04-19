import streamlit as st
import duckdb
import pandas as pd
import os

# Database Path Configuration
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'multibrand_retail.duckdb')

def inject_premium_css():
    """Injects custom CSS to improve dashboard aesthetics."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            font-size: 16px !important;
        }
        
        .main {
            background-color: #FAFAFA;
            color: #1F2937;
        }
        
        p, div, span, label {
            font-size: 1.1rem !important;
        }
        
        /* Metric Card Styling */
        [data-testid="stMetricValue"] {
            font-size: 2.8rem !important;
            font-weight: 700 !important;
            color: #0078D4 !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 1.2rem !important;
            font-weight: 600 !important;
            color: #6B7280 !important;
            text-transform: uppercase;
            letter-spacing: 0.05rem;
        }
        
        /* Typography */
        .main-header {
            background: linear-gradient(90deg, #0078D4 0%, #005A9E 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            font-size: 3.8rem;
            margin-bottom: 0rem;
        }
        
        section[data-testid="stSidebar"] {
            background-color: #F2F2F2;
            border-right: 1px solid #E5E7EB;
        }
        
        .js-plotly-plot {
            background-color: transparent !important;
        }
        </style>
        """, unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_data(query):
    """Executes a DuckDB query and returns a Pandas DataFrame."""
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    try:
        con = duckdb.connect(DB_PATH, read_only=True)
        df = con.execute(query).df()
        con.close()
        return df
    except Exception:
        return pd.DataFrame()

def check_db_state():
    """Checks if the analytical database exists and contains necessary tables."""
    if not os.path.exists(DB_PATH):
        st.error("Connection Error: Analytical database file not found.")
        return False
    
    tables = load_data("SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'")
    if tables.empty or 'fct_sales' not in tables['table_name'].values:
        st.warning("Data Integrity: Marts layer (Fact/Dimensions) not populated.")
        return False
    return True

def get_sidebar_filters():
    """Standardizes global filters across all dashboard pages."""
    st.sidebar.title("Filters")
    
    brands_df = load_data("SELECT DISTINCT brand_name FROM dim_products ORDER BY 1")
    brands = brands_df['brand_name'].tolist() if not brands_df.empty else []
    
    regions_df = load_data("SELECT DISTINCT region FROM dim_stores ORDER BY 1")
    regions = regions_df['region'].tolist() if not regions_df.empty else []
    
    if 'Digital/Online' not in regions:
        regions.append('Digital/Online')
    
    date_range_data = load_data("SELECT MIN(date) as start, MAX(date) as end FROM fct_sales")
    
    with st.sidebar:
        st.markdown("### Selection Scope")
        selected_brands = st.multiselect("Brands", brands, placeholder="All Brands")
        selected_regions = st.multiselect("Regions", regions, placeholder="All Regions")
        
        if not date_range_data.empty and date_range_data['start'][0] is not None:
            min_date = pd.to_datetime(date_range_data['start'][0]).date()
            max_date = pd.to_datetime(date_range_data['end'][0]).date()
            selected_dates = st.date_input("Period", value=(min_date, max_date), min_value=min_date, max_value=max_date)
        else:
            selected_dates = [None, None]
            
    # SQL Filter Construction
    where_clauses = []
    if selected_brands:
        brands_str = ", ".join([f"'{b}'" for b in selected_brands])
        where_clauses.append(f"p.brand_name IN ({brands_str})")
    if selected_regions:
        actual_regions = [r for r in selected_regions if r != 'Digital/Online']
        include_digital = 'Digital/Online' in selected_regions
        
        region_clauses = []
        if actual_regions:
            regions_str = ", ".join([f"'{r}'" for r in actual_regions])
            region_clauses.append(f"st.region IN ({regions_str})")
        if include_digital:
            region_clauses.append("st.region IS NULL")
            
        if region_clauses:
            where_clauses.append("(" + " OR ".join(region_clauses) + ")")
    if len(selected_dates) == 2 and selected_dates[0]:
        where_clauses.append(f"s.date BETWEEN '{selected_dates[0]}' AND '{selected_dates[1]}'")
    
    filter_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    return filter_sql
