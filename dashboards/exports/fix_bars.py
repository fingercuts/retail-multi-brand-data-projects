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
    
    # Update yaxes to be category type and ensure dtick=1
    content = content.replace("update_yaxes(dtick=1", "update_yaxes(type='category', dtick=1")
    
    # Update height multiplier from 25 to 45 for better spacing
    content = content.replace("* 25)", "* 45)")
    
    # Ensure bargap is set
    if 'bargap' not in content and 'px.bar' in content:
        content = content.replace("paper_bgcolor='rgba(0,0,0,0)',", "paper_bgcolor='rgba(0,0,0,0)', bargap=0.2,")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Bar chart alignment and thickness fixed across all pages.")
