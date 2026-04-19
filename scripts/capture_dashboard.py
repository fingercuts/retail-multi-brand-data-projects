import os
import time
from playwright.sync_api import sync_playwright

def capture_streamlit_dashboard():
    print("Initiating Playwright to capture the Retail Multi-Brand Dashboard...")
    
    # Output directory standard matching the newly established Docs/Assets pattern
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'docs', 'assets'))
    os.makedirs(output_dir, exist_ok=True)
    
    # Target URLs mapping to Streamlit multi-page routes
    base_url = "http://localhost:8501"
    pages = {
        "Home": "",
        "Executive_Overview": "Executive_Overview",
        "Business_Operations": "Business_Operations",
        "Product_Insights": "Product_Insights",
        "Customer_Analytics": "Customer_Analytics",
        "Promotion_Analysis": "Promotion_Analysis"
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        for idx, (page_name, route) in enumerate(pages.items()):
            url = f"{base_url}/{route}"
            screenshot_name = f"screenshot_{idx}_{page_name.lower()}.png"
            screenshot_path = os.path.join(output_dir, screenshot_name)
            
            try:
                print(f"-> Navigating to {url}...")
                page.goto(url, wait_until="networkidle", timeout=20000)
                
                print(f"-> Waiting for Streamlit UI to render on {page_name}...")
                page.wait_for_selector(".stApp", state="visible", timeout=20000)
                
                # Plotly and dynamic DuckDB fetching requires extra buffering
                time.sleep(5)
                
                # Overflow lock bypass via raw JS injection
                page.evaluate("""
                    const selectors = ['.main', '.block-container', 'section'];
                    document.querySelectorAll(selectors.join(', ')).forEach(e => {
                        if (e) {
                            e.style.height = 'auto';
                            e.style.overflow = 'visible';
                        }
                    });
                """)
                time.sleep(1)
                
                # Execute full shutter snap
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"Success! {page_name} snapshot saved to {screenshot_path}")
            
            except Exception as e:
                print(f"ERROR capturing {page_name}: {e}")
                
        browser.close()

if __name__ == "__main__":
    capture_streamlit_dashboard()
