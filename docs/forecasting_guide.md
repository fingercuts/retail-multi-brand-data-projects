# Forecasting Guide: Sales Demand Modeling

This project uses the **Facebook Prophet** library to generate 90-day sales forecasts. The model is designed to help business stakeholders anticipate demand spikes and optimize inventory routing across regional warehouses.

## Implementation Overview
The forecasting logic is contained in `notebooks/03_forecasting.ipynb`. It pulls cleaned sales data from the `fact_sales` table in DuckDB and aggregates it into a daily time series.

### Key Components of the Model:
- **Trend**: Measures the underlying growth or decline of the retail brand, independent of seasonal noise.
- **Weekly Seasonality**: Captures the recurring patterns of the 7-day sales cycle (typically peaks on weekends).
- **Yearly Seasonality**: Models the large-scale shifts caused by seasons and fiscal quarters.
- **Holidays**: The model is tuned to account for major retail events (e.g., Black Friday, Christmas, Eid al-Fitr) which cause significant short-term deviations from the baseline trend.

---

## Interpreting the Forecast

### Uncertainty Intervals
The forecast includes a shaded "uncertainty interval" (defaulted to 80%). 
- If actual sales fall **inside** the shaded area, the business is performing as expected.
- If actual sales fall **outside** the shaded area, it indicates an anomaly—usually a highly successful promotion, a local supply chain failure, or a sudden shift in consumer behavior that requires investigation.

### Seasonality & Marketing
By reviewing the **Components Plot**, marketing teams can identify the exact "lead up" period before a seasonal peak. 
- *Strategy*: If the model predicts a yearly peak starting on December 1st, marketing campaigns should be front-loaded in late November to maximize the capture of that demand.

---

## Maintenance & Tuning
To update the forecast with the latest data:
1. Ensure the dbt models have been run (`make dbt-build`).
2. Run the `03_forecasting.ipynb` notebook.
3. If accuracy decreases, consider adding "Regressors" (extra columns like local weather or promotion flags) using the `m.add_regressor()` function within the notebook.
