import os
import re

pages_info = {
    '01_Executive_Overview.py': ("Executive Overview", "Corporate Key Performance Indicators & Revenue Velocity"),
    '02_Business_Operations.py': ("Business Operations", "Regional Performance & Operational Efficiency"),
    '03_Product_Insights.py': ("Product & Inventory", "SKU Performance, Pricing Analysis & Inventory Health"),
    '04_Customer_Analytics.py': ("Customer Intelligence", "Demographic Segmentation & Geographic Distribution"),
    '05_Promotion_Analysis.py': ("Promotion & Marketing", "Campaign Effectiveness & Discount Impact Analysis")
}

needed_imports = [
    'render_premium_header', 'load_data', 'inject_premium_css', 
    'check_db_state', 'get_sidebar_filters', 'format_currency', 
    'PBI_PALETTE', 'pbi_chart_layout', 'format_number'
]

for filename, (title, subtitle) in pages_info.items():
    filepath = f'dashboards/pages/{filename}'
    if not os.path.exists(filepath): continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Standardize Imports from utils_dashboard
    import_pattern = r'from utils_dashboard import .*'
    standardized_import = f"from utils_dashboard import {', '.join(needed_imports)}"
    content = re.sub(import_pattern, standardized_import, content)
    
    # 2. Force Premium Header migration if not already done
    if 'render_premium_header' not in content or 'main-header' in content:
        # Replace manual header blocks
        header_pattern = r'# --- HEADER ---.*?st\.markdown\(f?\"<p.*?</p>\", unsafe_allow_html=True\)'
        new_header = f'# --- HEADER ---\n    render_premium_header("{title}", "{subtitle}")'
        content = re.sub(header_pattern, new_header, content, flags=re.DOTALL)

    # 3. Fix Palette typos
    content = content.replace('PBI_PALETTE2', 'PBI_PALETTE')
    
    # 4. Cleanup any remaining long labels dictionaries
    long_labels_pattern = r"labels=\{'brand_name': 'Brand', 'revenue': 'Revenue', 'category': 'Category', 'channel': 'Channel', 'region': 'Region', 'age_group': 'Age Group', 'customers': 'Customers', 'city': 'City', 'gender': 'Gender', 'promo_status': 'Promotion Status', 'discount_pct': 'Discount %', 'day': 'Date', 'price': 'Price', 'margin': 'Margin'\}"
    content = content.replace(long_labels_pattern, "labels={'brand_name': 'Brand', 'revenue': 'Revenue', 'units': 'Units Sold', 'region': 'Region', 'channel': 'Channel'}")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("All dashboard pages have been standardized and fixed.")
