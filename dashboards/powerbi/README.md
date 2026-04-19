# Power BI Integration

This directory contains the Power BI reporting templates (`.pbix`) and documentation for the OmniRetail analytics platform.

## 🚀 Live Analytical Access
Access the interactive web-hosted dashboard here: **[Link to Live Power BI Dashboard]**

## Data Source Configuration
The dashboard is designed to connect to the dbt-generated Parquet files in `data/marts/` or the combined DuckDB database.

### Initial Setup
1.  **Generate Data**: Ensure the local database has been built using `make ingest` and `make dbt-build`.
2.  **Open Template**: Open the `.pbix` file in Power BI Desktop.
3.  **Update File Paths**:
    - If you are opening this for the first time in a new environment, you must update the local file path pointers.
    - Navigate to **File > Options and settings > Data source settings**.
    - Select the source(s) and click **Change Source**.
    - Browse to your local `retail-multi-brand-data-projects/data/` directory and select the appropriate source.
4.  **Refresh**: Click **Refresh** to populate the visuals with your local dataset.

## Version Control Note
Large binary files like `.pbix` are often stored with data cleared to minimize repository size. If you make changes to the report layout, prefer saving the file after a "Clear Data" operation to keep the commit size small, or utilize Git LFS for full binary versioning.

---

## Analytical Semantic Layer (DAX)
While 90% of business logic is handled in the **dbt** semantic layer, the following DAX measures are utilized to enable dynamic executive reporting and advanced time-intelligence within Power BI. 

### 1. Sales Year-over-Year (YoY) Growth %
Used for comparing current period performance against the same period in the previous fiscal year.
```dax
Sales YoY Growth % = 
VAR PreviousYearSales = CALCULATE([Total Revenue], SAMEPERIODLASTYEAR('Calendar'[Date]))
RETURN
DIVIDE([Total Revenue] - PreviousYearSales, PreviousYearSales, 0)
```

### 2. 30-Day Moving Average
Calculated to smooth out short-term fluctuations and identify genuine sales trends across brand categories.
```dax
30-Day Sales Moving Avg = 
AVERAGEX(
    DATESINPERIOD('Calendar'[Date], LASTDATE('Calendar'[Date]), -30, DAY),
    [Total Revenue]
)
```

### 3. Dynamic Metric Toggle
Enables stakeholders to switch entire report pages between **Revenue**, **Units**, and **Avg. Order Value** using a single slicer.
```dax
Target Metric = 
VAR Selection = SELECTEDVALUE('Metric Selection'[Metric])
RETURN
SWITCH(Selection,
    "Revenue", [Total Revenue],
    "Units", [Total Units],
    "Avg. Order Value", DIVIDE([Total Revenue], [Total Transactions]),
    [Total Revenue]
)
```
