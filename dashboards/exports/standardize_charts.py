import os
import re

pages = [
    '01_Executive_Overview.py',
    '02_Business_Operations.py',
    '03_Product_Insights.py',
    '04_Customer_Analytics.py',
    '05_Promotion_Analysis.py'
]

for filename in pages:
    filepath = f'dashboards/pages/{filename}'
    if not os.path.exists(filepath): continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Ensure PBI_PALETTE is imported
    if 'PBI_PALETTE' not in content:
        content = content.replace('from utils_dashboard import', 'from utils_dashboard import PBI_PALETTE,')
    
    # 2. Replace color sequences with PBI_PALETTE
    # Matches px.colors.qualitative.XXX
    content = re.sub(r'color_discrete_sequence=px\.colors\.qualitative\.[a-zA-Z]+', 'color_discrete_sequence=PBI_PALETTE', content)
    
    # 3. Clean up the oversized labels dictionary
    # Matches the long labels={...} string often found in these charts
    long_labels_pattern = r"labels=\{'brand_name': 'Brand', 'revenue': 'Revenue', 'category': 'Category', 'channel': 'Channel', 'region': 'Region', 'age_group': 'Age Group', 'customers': 'Customers', 'city': 'City', 'gender': 'Gender', 'promo_status': 'Promotion Status', 'discount_pct': 'Discount %', 'day': 'Date', 'price': 'Price', 'margin': 'Margin'\}"
    
    # We replace it with a more focused labels dict or just empty if we want to be safe, but let's keep relevant ones.
    # Actually, most charts only need a few. I'll just remove the redundant ones.
    content = content.replace(long_labels_pattern, "labels={'brand_name': 'Brand', 'revenue': 'Revenue', 'units': 'Units Sold', 'region': 'Region', 'channel': 'Channel'}")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("All pages migrated to PBI_PALETTE and labels cleaned.")
