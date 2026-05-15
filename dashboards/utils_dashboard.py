import streamlit as st
import duckdb
import pandas as pd
import os

# Database Path Configuration
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'multibrand_retail.duckdb')

# ─── Power BI Design Tokens ────────────────────────────────────────────────────
PBI_COLORS = {
    "bg_canvas":      "#F4F6F9",
    "bg_card":        "#FFFFFF",
    "bg_card_hover":  "#FAFAFA",
    "bg_sidebar":     "#2B2A3D",
    "accent":         "#F2C811",   # Power BI signature yellow
    "accent_blue":    "#118DFF",   # Power BI primary blue
    "accent_teal":    "#12B5CB",
    "accent_purple":  "#A855F7",
    "accent_green":   "#00B8A9",
    "accent_red":     "#E23636",
    "text_primary":   "#1E293B",
    "text_secondary": "#475569",
    "text_muted":     "#94A3B8",
    "border":         "#E2E8F0",
    "kpi_bg":         "#2B2A3D",   # Dark KPI cards
    "kpi_value":      "#FFFFFF",
    "kpi_label":      "#F1F5F9",
}

PBI_PALETTE = [
    "#118DFF", "#12B5CB", "#E66C37", "#6B007B",
    "#E044A7", "#744EC2", "#D9B300", "#D64550",
    "#197278", "#1AAB40", "#F2C80F", "#FF6B6B",
]

def pbi_chart_layout(title="", height=400, show_legend=True):
    """Returns a standardized Power BI-style Plotly layout dict."""
    layout = dict(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(t=30, b=40, l=50, r=20),
        font=dict(family="Segoe UI, sans-serif", size=12, color=PBI_COLORS["text_secondary"]),
        showlegend=show_legend,
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5,
            font=dict(size=11, color=PBI_COLORS["text_secondary"]),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(
            gridcolor="rgba(0,0,0,0.06)", zerolinecolor="rgba(0,0,0,0)",
            tickfont=dict(color="#475569"),
        ),
        yaxis=dict(
            gridcolor="rgba(0,0,0,0.06)", zerolinecolor="rgba(0,0,0,0)",
            tickfont=dict(color="#475569"),
        ),
        hoverlabel=dict(bgcolor="#FFFFFF", font_size=12, font_family="Segoe UI, sans-serif", font_color="#1E293B", bordercolor="#E2E8F0"),
        colorway=PBI_PALETTE,
    )
    if title:
        layout['title'] = dict(text=title, font=dict(family="Segoe UI, sans-serif", size=14, color=PBI_COLORS["text_primary"]), x=0, y=0.98)
    return layout

def inject_premium_css():
    """Injects Power BI-inspired CSS to completely restyle Streamlit into a Premium Light Mode."""
    st.markdown("""
        <style>
        /* ──── FONTS ─────────────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@300;400;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Segoe UI', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

        /* ──── CANVAS ────────────────────────────────────────── */
        .stApp, .main .block-container {
            background-color: #F4F6F9 !important;
            color: #1E293B !important;
        }

        .main .block-container {
            padding: 1.5rem 2rem 2rem 2rem !important;
            max-width: 100% !important;
        }

        /* ──── HIDE STREAMLIT BRANDING ───────────────────────── */
        #MainMenu, footer, header[data-testid="stHeader"],
        .stDeployButton, [data-testid="stStatusWidget"],
        button[kind="header"] {
            display: none !important;
            visibility: hidden !important;
        }

        /* ──── SIDEBAR — Power BI Nav Pane ───────────────────── */
        [data-testid="stSidebarNav"]::before {
            content: "⬡ OmniRetail Analytics";
            display: block;
            color: #F2C811;
            font-weight: 700;
            font-size: 0.95rem;
            padding: 24px 16px 12px 16px;
            letter-spacing: 0.5px;
        }

        [data-testid="stSidebarNav"]::before {
            content: "⬡ OmniRetail Analytics";
            display: block;
            color: #F2C811;
            font-weight: 700;
            font-size: 1.1rem;
            padding: 24px 24px 12px 24px;
            letter-spacing: 0.5px;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #2D2B3D 0%, #252433 100%) !important;
            border-right: 1px solid #1A1A24 !important;
            width: 260px !important;
        }

        section[data-testid="stSidebar"] .stMarkdown h1,
        section[data-testid="stSidebar"] .stMarkdown h2,
        section[data-testid="stSidebar"] .stMarkdown h3 {
            color: #F2C811 !important;
            font-weight: 600 !important;
            font-size: 0.85rem !important;
            text-transform: uppercase !important;
            letter-spacing: 1.5px !important;
            margin-bottom: 0.3rem !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
            color: #A0B0C0 !important;
            font-size: 0.92rem !important;
            padding: 10px 16px !important;
            border-radius: 6px !important;
            transition: all 0.2s ease !important;
            border-left: 4px solid transparent !important;
            margin: 4px 12px !important;
            width: auto !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
            background: rgba(255,255,255,0.08) !important;
            color: #FFFFFF !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-selected="true"] {
            background: #FFFFFF !important;
            color: #2D2B3D !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
            border-left: 4px solid #F2C811 !important;
        }

        section[data-testid="stSidebar"] .stMultiSelect,
        section[data-testid="stSidebar"] .stDateInput {
            background: transparent !important;
        }

        section[data-testid="stSidebar"] label {
            color: #8C9BAB !important;
            font-size: 0.8rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
        }

        /* ──── KPI / METRIC CARDS ────────────────────────────── */
        [data-testid="stMetric"] {
            background: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 10px !important;
            padding: 20px 24px !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
            transition: all 0.2s ease !important;
        }

        [data-testid="stMetric"]:hover {
            border-color: #F2C811 !important;
            box-shadow: 0 6px 16px rgba(242,200,17,0.15) !important;
            transform: translateY(-2px) !important;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.85rem !important;
            font-weight: 700 !important;
            color: #1E293B !important;
            letter-spacing: -0.5px !important;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.75rem !important;
            font-weight: 600 !important;
            color: #64748B !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
        }

        [data-testid="stMetricDelta"] {
            font-size: 0.8rem !important;
            color: #475569 !important;
        }

        /* ──── CARD CONTAINERS (for charts) ──────────────────── */
        [data-testid="stVerticalBlock"] > div > div[data-testid="stVerticalBlockBorderWrapper"] {
            background: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.04) !important;
        }

        /* ──── SECTION TITLES ────────────────────────────────── */
        .pbi-section-title {
            color: #1E293B !important;
            font-size: 0.85rem !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 1.2px !important;
            padding-bottom: 6px !important;
            margin-bottom: 12px !important;
            border-bottom: 2px solid #F2C811 !important;
            display: inline-block !important;
        }

        .pbi-page-title {
            color: #1E293B !important;
            font-size: 1.6rem !important;
            font-weight: 600 !important;
            letter-spacing: -0.3px !important;
            margin-bottom: 2px !important;
        }

        .pbi-page-subtitle {
            color: #475569 !important;
            font-size: 0.85rem !important;
            font-weight: 400 !important;
            letter-spacing: 0.3px !important;
            margin-bottom: 16px !important;
        }

        /* ──── PLOTLY CHART WRAPPERS ─────────────────────────── */
        .pbi-chart-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.04);
            transition: box-shadow 0.2s ease, border-color 0.2s ease;
        }

        .pbi-chart-card:hover {
            border-color: #CBD5E1;
            box-shadow: 0 6px 20px rgba(0,0,0,0.06);
        }

        .pbi-chart-title {
            color: #1E293B !important;
            font-size: 0.82rem !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.8px !important;
            margin-bottom: 8px !important;
        }

        /* ──── DATA TABLES ───────────────────────────────────── */
        [data-testid="stDataFrame"], .stDataFrame {
            background: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 8px !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.04) !important;
        }

        [data-testid="stDataFrame"] table {
            background: #FFFFFF !important;
        }

        [data-testid="stDataFrame"] th {
            background: #F8FAFC !important;
            color: #475569 !important;
            font-size: 0.75rem !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
            border-bottom: 2px solid #E2E8F0 !important;
        }

        [data-testid="stDataFrame"] td {
            color: #334155 !important;
            font-size: 0.85rem !important;
            border-bottom: 1px solid #F1F5F9 !important;
        }

        /* ──── DIVIDERS ──────────────────────────────────────── */
        hr {
            border-color: #E2E8F0 !important;
            margin: 12px 0 !important;
        }

        /* ──── MULTISELECT & INPUTS ──────────────────────────── */
        .stMultiSelect > div, .stDateInput > div {
            background: rgba(255,255,255,0.05) !important;
            border-color: #4B5563 !important;
            border-radius: 6px !important;
        }

        .stMultiSelect [data-baseweb="tag"] {
            background: rgba(242,200,17,0.15) !important;
            color: #F2C811 !important;
            border: 1px solid rgba(242,200,17,0.3) !important;
        }

        /* ──── SCROLLBAR ─────────────────────────────────────── */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #94A3B8; }

        /* ──── ALERT BOXES ───────────────────────────────────── */
        [data-testid="stAlert"] {
            background: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 8px !important;
            color: #1E293B !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.04) !important;
        }

        /* ──── PLOTLY TRANSPARENT ─────────────────────────────── */
        .js-plotly-plot {
            background-color: transparent !important;
        }

        /* ──── POWER BI FOOTER BAR ───────────────────────────── */
        .pbi-footer {
            position: fixed;
            bottom: 0;
            left: 260px;
            right: 0;
            height: 28px;
            background: #FFFFFF;
            border-top: 1px solid #E2E8F0;
            display: flex;
            align-items: center;
            padding: 0 16px;
            z-index: 999;
            font-size: 0.7rem;
            color: #64748B;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.02);
        }

        .pbi-footer-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #00B8A9;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }

        /* ──── LANDING PAGE CARDS ────────────────────────────── */
        .pbi-module-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 24px;
            height: 180px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.25s ease;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.04);
        }

        .pbi-module-card:hover {
            border-color: #F2C811;
            box-shadow: 0 8px 25px rgba(242,200,17,0.15);
            transform: translateY(-3px);
        }

        .pbi-module-icon {
            font-size: 2rem;
            margin-bottom: 12px;
        }

        .pbi-module-title {
            color: #1E293B;
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 6px;
        }

        .pbi-module-desc {
            color: #475569;
            font-size: 0.78rem;
            line-height: 1.4;
        }

        /* ──── STATUS BADGES ─────────────────────────────────── */
        .pbi-status-connected {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(0,184,169,0.12);
            color: #009688;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.3px;
        }

        .pbi-status-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #00B8A9;
        }

        </style>
    """, unsafe_allow_html=True)


def format_currency(value):
    """Formats a number into abbreviated format with dynamic currency."""
    if pd.isna(value) or value is None:
        value = 0

    currency = st.session_state.get('selected_currency', 'USD')
    
    # Conversion rates (Static approximations for reporting)
    rates = {"IDR": 1, "USD": 1/15500, "EUR": 1/16500}
    symbols = {"IDR": "Rp", "USD": "$", "EUR": "€"}
    
    val = value * rates.get(currency, 1)
    sym = symbols.get(currency, "Rp")
    abs_val = abs(val)
    
    if abs_val >= 1_000_000_000_000:
        formatted = f"{sym} {val / 1_000_000_000_000:.1f}T"
    elif abs_val >= 1_000_000_000:
        formatted = f"{sym} {val / 1_000_000_000:.1f}B"
    elif abs_val >= 1_000_000:
        formatted = f"{sym} {val / 1_000_000:.1f}M"
    elif abs_val >= 1_000:
        formatted = f"{sym} {val / 1_000:.1f}K"
    else:
        formatted = f"{sym} {val:,.0f}"

    return formatted.replace(".0T", "T").replace(".0B", "B").replace(".0M", "M").replace(".0K", "K")


def format_number(value):
    """Formats a number into abbreviated format (e.g. 1.5M, 800.3K)."""
    if pd.isna(value) or value is None:
        return "0"

    abs_val = abs(value)
    if abs_val >= 1_000_000_000_000:
        formatted = f"{value / 1_000_000_000_000:.1f}T"
    elif abs_val >= 1_000_000_000:
        formatted = f"{value / 1_000_000_000:.1f}B"
    elif abs_val >= 1_000_000:
        formatted = f"{value / 1_000_000:.1f}M"
    elif abs_val >= 1_000:
        formatted = f"{value / 1_000:.1f}K"
    else:
        formatted = f"{value:,.0f}"

    return formatted.replace(".0T", "T").replace(".0B", "B").replace(".0M", "M").replace(".0K", "K")


def render_pbi_header(title, subtitle=""):
    """Renders a Power BI-style page header."""
    st.markdown(f'<div class="pbi-page-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="pbi-page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def render_premium_header(title, subtitle):
    """Renders a high-fidelity top ribbon with title, subtitle, and currency selector."""
    col1, col2 = st.columns([0.75, 0.25])
    with col1:
        st.markdown(f'<h1 class="main-header" style="margin-bottom:0; padding-bottom:0;">{title}</h1>', unsafe_allow_html=True)
        st.markdown(f"<p style='color: #94a3b8; font-size: 1.1rem; margin-top:0; padding-top:0;'>{subtitle}</p>", unsafe_allow_html=True)
    with col2:
        # Reverting to selectbox as requested, with a fix for the font color
        st.markdown("""
            <style>
                /* Target the specific selectbox in the header to ensure dark text on light bg */
                div[data-testid="stSelectbox"] label p {
                    color: #475569 !important;
                    font-weight: 600 !important;
                }
                /* CSS hack to make the selectbox input feel less 'editable' by hiding the cursor */
                div[data-testid="stSelectbox"] input {
                    caret-color: transparent !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        selected_currency = st.selectbox(
            "💱 Currency", 
            ["USD", "IDR", "EUR"], 
            index=0,
            key="selected_currency", 
            help="Switch reporting currency"
        )



    st.markdown("<hr style='margin-top:0; margin-bottom:20px; border:0; border-top:1px solid #E2E8F0;'>", unsafe_allow_html=True)


def render_pbi_section(title):
    """Renders a Power BI-style section title with gold underline."""
    st.markdown(f'<div class="pbi-section-title">{title}</div>', unsafe_allow_html=True)


def render_pbi_footer():
    """Renders a Power BI-style footer status bar."""
    st.markdown("""
        <div class="pbi-footer">
            <span class="pbi-footer-dot"></span>
            <span>Data refresh: Live &nbsp;&bull;&nbsp; DuckDB Analytical Engine &nbsp;&bull;&nbsp; OmniRetail Holdings</span>
        </div>
    """, unsafe_allow_html=True)


def chart_card_start(title=""):
    """Starts a Power BI-style chart card container."""
    title_html = f'<div class="pbi-chart-title">{title}</div>' if title else ""
    st.markdown(f'<div class="pbi-chart-card">{title_html}', unsafe_allow_html=True)


def chart_card_end():
    """Closes a Power BI-style chart card container."""
    st.markdown('</div>', unsafe_allow_html=True)


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
        return False

    tables = load_data("SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'")
    if tables.empty or 'fct_sales' not in tables['table_name'].values:
        return False
    return True

def get_sidebar_filters():
    """Standardizes global filters across all dashboard pages — Power BI filter pane style."""
    
    # 1. Data Loading for Filters
    brands_df = load_data("SELECT DISTINCT brand_name FROM dim_products ORDER BY 1")
    brands = brands_df['brand_name'].tolist() if not brands_df.empty else []

    regions_df = load_data("SELECT DISTINCT region FROM dim_stores ORDER BY 1")
    regions = regions_df['region'].tolist() if not regions_df.empty else []
    if 'Digital/Online' not in regions:
        regions.append('Digital/Online')

    date_range_data = load_data("SELECT MIN(date) as start, MAX(date) as end FROM fct_sales")

    # 2. Filter Controls
    with st.sidebar:
        st.markdown("### ⚡ Filters")
        selected_brands = st.multiselect("Brand", brands, placeholder="All Brands")
        selected_regions = st.multiselect("Region", regions, placeholder="All Regions")

        if not date_range_data.empty and date_range_data['start'][0] is not None:
            min_date = pd.to_datetime(date_range_data['start'][0]).date()
            max_date = pd.to_datetime(date_range_data['end'][0]).date()
            selected_dates = st.date_input("Period", value=(min_date, max_date), min_value=min_date, max_value=max_date)
        else:
            selected_dates = [None, None]

        st.markdown("---")

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
