# Reporting Reference: Business Metrics & Insights

This guide defines the key performance indicators (KPIs) and analytical frameworks supported by the Retail Multi-Brand warehouse. Use these metrics as the foundation for BI reports and executive presentations.

## 1. Sales & Revenue
- **Gross Revenue (`total_amount`)**: Total raw value of transactions before any discounts or adjustments.
- **Net Revenue (`net_amount`)**: The actual realized revenue after applying promotions and taxes. This is the primary top-line metric.
- **Average Transaction Value (ATV)**: Calculated as `SUM(net_amount) / COUNT(DISTINCT transaction_id)`.
- **Sales Volume**: Total `units_sold`.

## 2. Customer Performance
- **Retention Rate**: The percentage of customers from a specific join-month cohort who shop again in subsequent months.
- **Customer Lifetime Value (LTV)**: Predictive and historical analysis of a customer's total spend across multiple brands.
- **Regional Contribution**: Revenue broken down by customer geography (`region`, `city`).

## 3. Product & Brand Metrics
- **Category Mix**: Distribution of sales across product categories (e.g., Electronics vs. Apparel).
- **Brand Loyalty**: Analyzing how many customers shop across multiple brands (the "Omnichannel Multiplier").
- **Sell-Through Rate**: Ratio of units sold compared to total stock on hand, used to identify slow-moving inventory.

## 4. Promotion ROI
- **Promo Lift**: The increase in sales volume during a promotional window compared to the baseline period immediately prior.
- **Redemption Rate**: The percentage of total sales attributed to a specific `promotion_id`.
- **Margin Erosion**: Tracking the impact of deep discounts (`discount_pct`) on overall net profitability.

## 5. Inventory Efficiency
- **Stock-to-Sales Ratio**: Monthly units sold divided by units on hand. High ratios suggest a risk of stockouts.
- **Dead Stock Identification**: Flagging SKUs with zero sales in the last 30/60 days.

## 6. Connectivity for BI Tools
The analytical layer resides in **DuckDB**.

### Local BI (Power BI / Tableau)
The recommended connection method is via the **DuckDB ODBC Driver**:
1.  Configure a DSN pointing to `data/multibrand_retail.duckdb`.
2.  Import tables like `fct_sales` and `dim_customers`.

### Web Reporting
For browser-based tools, export clean tables to Parquet or CSV for ingestion into a cloud-based serving layer like BigQuery or Snowflake.
