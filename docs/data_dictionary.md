# 📑 Data Dictionary

This project has 3 main layers of data:

- **Raw Layer (`raw_*`)** → Direct CSV extracts, untouched, messy formats.
- **Staging Layer (`stg_*`)** → Parquet-converted raw data, lightly cleaned, query-ready.
- **Marts Layer (`dim_*`, `fact_*`)** → Star schema models built in dbt, analytics-ready.

---

## 🔹 Raw Layer (CSV extracts)

+------------------+---------------------+-----------------------------------------------+-----------+
| Table            | Column              | Description                                   | Type      |
+------------------+---------------------+-----------------------------------------------+-----------+
| raw_customers    | customer_id         | Unique ID per customer                        | string    |
|                  | name                | Full name of customer                         | string    |
|                  | gender              | Gender (may include values like M, F)         | string    |
|                  | age                 | Age of customer (nullable in raw)             | int       |
|                  | city                | City of residence (messy formatting possible) | string    |
|                  | region              | Region/province                               | string    |
+------------------+---------------------+-----------------------------------------------+-----------+
| raw_products     | product_id          | Unique product ID                             | string    |
|                  | product_name        | Product label                                 | string    |
|                  | brand_id            | Foreign key to raw_brands                     | string    |
|                  | category            | Product category                              | string    |
|                  | price               | Price (missing/outlier values possible)       | decimal   |
+------------------+---------------------+-----------------------------------------------+-----------+
| raw_brands       | brand_id            | Brand unique ID                               | string    |
|                  | brand_name          | Brand name                                    | string    |
|                  | category            | Brand’s main business category                | string    |
+------------------+---------------------+-----------------------------------------------+-----------+
| raw_stores       | store_id            | Unique ID for store                           | string    |
|                  | store_name          | Store label (name + city)                     | string    |
|                  | brand_id            | Foreign key to raw_brands                     | string    |
|                  | city                | Store city                                    | string    |
|                  | region              | Store region/province                         | string    |
|                  | channel             | Offline/Online classification                 | string    |
|                  | opening_year        | Year store opened                             | int       |
|                  | closing_year        | Closing year (nullable if active)             | int       |
|                  | status              | Active / Closed                               | string    |
+------------------+---------------------+-----------------------------------------------+-----------+
| raw_sales        | date                | Transaction datetime                          | datetime  |
|                  | customer_id         | FK to raw_customers                           | string    |
|                  | product_id          | FK to raw_products                            | string    |
|                  | store_id            | FK to raw_stores                              | string    |
|                  | promotion_id        | FK to raw_promotions                          | string    |
|                  | units_sold          | Number of products sold                       | int       |
|                  | total_amount        | Gross amount                                  | decimal   |
|                  | discounted_amount   | Discount value applied                        | decimal   |
+------------------+---------------------+-----------------------------------------------+-----------+
| raw_promotions   | promotion_id        | Promo unique ID                               | string    |
|                  | promo_name          | Promo name                                    | string    |
|                  | type                | Promo type (seasonal/voucher/etc.)            | string    |
|                  | discount_pct        | Discount percentage                           | decimal   |
|                  | start_date          | Promo start                                   | datetime  |
|                  | end_date            | Promo end                                     | datetime  |
+------------------+---------------------+-----------------------------------------------+-----------+
| raw_inventory    | store_id            | FK to raw_stores                              | string    |
|                  | product_id          | FK to raw_products                            | string    |
|                  | stock_on_hand       | Current stock                                 | int       |
|                  | reorder_level       | Min stock before reorder                      | int       |
|                  | last_restocked_date | Last restocking date                          | datetime  |
+------------------+---------------------+-----------------------------------------------+-----------+
| raw_channels     | channel_id          | Unique channel ID                             | string    |
|                  | channel_name        | E.g., Website, Shopee, Tokopedia              | string    |
|                  | type                | Channel type: E-commerce / Marketplace        | string    |
+------------------+---------------------+-----------------------------------------------+-----------+

---

## 🔹 Staging Layer (Parquet)

⚡ Same schema as raw tables, but optimized and standardized in Parquet for DuckDB/dbt.  

+----------------+--------------------------------+
| Staging Table  | Data Source                    |
+----------------+--------------------------------+
| stg_customers  | raw_customers (CSV → Parquet)  |
| stg_products   | raw_products (CSV → Parquet)   |
| stg_brands     | raw_brands (CSV → Parquet)     |
| stg_stores     | raw_stores (CSV → Parquet)     |
| stg_sales      | raw_sales (CSV → Parquet)      |
| stg_promotions | raw_promotions (CSV → Parquet) |
| stg_inventory  | raw_inventory (CSV → Parquet)  |
| stg_channels   | raw_channels (CSV → Parquet)   |
+----------------+--------------------------------+

---

## 🔹 Marts Layer (Star Schema)

+-----------------+-------------------+-------------------------------------------+----------+
| Table           | Column            | Description                               | Type     |
+-----------------+-------------------+-------------------------------------------+----------+
| fact_sales      | date              | Transaction date                          | datetime |
|                 | customer_id       | FK → dim_customers                        | string   |
|                 | product_id        | FK → dim_products                         | string   |
|                 | brand_id          | FK → dim_brands                           | string   |
|                 | store_id          | FK → dim_stores                           | string   |
|                 | promotion_id      | FK → dim_promotions                       | string   |
|                 | units_sold        | Units sold                                | int      |
|                 | total_amount      | Revenue before discount                   | decimal  |
|                 | discounted_amount | Discount amount applied                   | decimal  |
+-----------------+-------------------+-------------------------------------------+----------+
| dim_customers   | customer_id       | Unique ID                                 | string   |
|                 | name              | Customer name                             | string   |
|                 | gender            | Gender                                    | string   |
|                 | age               | Age                                       | int      |
|                 | city              | City                                      | string   |
|                 | region            | Region                                    | string   |
+-----------------+-------------------+-------------------------------------------+----------+
| dim_products    | product_id        | Unique ID                                 | string   |
|                 | product_name      | Name                                      | string   |
|                 | category          | Category                                  | string   |
|                 | price             | Price                                     | decimal  |
|                 | brand_id          | FK → dim_brands                           | string   |
|                 | brand_name        | Brand                                     | string   |
+-----------------+-------------------+-------------------------------------------+----------+
| dim_brands      | brand_id          | Unique ID                                 | string   |
|                 | brand_name        | Brand                                     | string   |
|                 | category          | Category                                  | string   |
+-----------------+-------------------+-------------------------------------------+----------+
| dim_stores      | store_id          | Unique store ID                           | string   |
|                 | store_name        | Store label                               | string   |
|                 | brand_id          | Brand link                                | string   |
|                 | region            | Region                                    | string   |
|                 | channel           | Offline/Online                            | string   |
|                 | status            | Active/Closed                             | string   |
+-----------------+-------------------+-------------------------------------------+----------+
| dim_promotions  | promotion_id      | Unique ID                                 | string   |
|                 | promo_name        | Name                                      | string   |
|                 | type              | Seasonal/Voucher                          | string   |
|                 | discount_pct      | % applied                                 | decimal  |
|                 | start_date        | Start date                                | datetime |
|                 | end_date          | End date                                  | datetime |
+-----------------+-------------------+-------------------------------------------+----------+


---