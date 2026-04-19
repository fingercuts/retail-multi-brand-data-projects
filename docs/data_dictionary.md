# Data Dictionary: Retail Multi-Brand Platform

This repository organizes data into three distinct architectural layers. This document defines the schemas and data types for each layer.

## 1. Raw Layer (Source CSVs)
These are direct extracts from the brand subsidiaries. They contain messy formats, inconsistent casing, and unmasked PII.

### Customers (`raw_customers`)
| Column | Type | Description |
| :--- | :--- | :--- |
| `customer_id` | string | Primary key from the source CRM. |
| `name` | string | Raw full name (unmasked). |
| `gender` | string | Genders (M/F/O). |
| `age` | int | Customer age at time of extract. |
| `city` | string | City of residence (non-standardized). |
| `region` | string | Geographic region. |

### Sales (`raw_sales`)
| Column | Type | Description |
| :--- | :--- | :--- |
| `date` | datetime | ISO timestamp of the transaction. |
| `customer_id` | string | Foreign key to `raw_customers`. |
| `product_id` | string | Foreign key to `raw_products`. |
| `store_id` | string | Foreign key to `raw_stores`. |
| `units_sold` | int | Quantity purchased. |
| `total_amount` | decimal | Gross amount before discounts. |
| `discounted_amount`| decimal | Value of total discount applied. |

*(Other raw tables including `raw_products`, `raw_brands`, `raw_stores`, `raw_promotions`, `raw_inventory`, and `raw_channels` follow a similar direct-extract schema.)*

---

## 2. Staging Layer (Parquet)
The staging layer replicates the raw schema but converts all files to **Parquet** format. This layer standardizes data types (dates, decimals) and allows for high-performance reading by dbt and DuckDB.

| Table | Source |
| :--- | :--- |
| `stg_customers` | `raw_customers` |
| `stg_sales` | `raw_sales` |
| `stg_products` | `raw_products` |
| ... | ... |

---

## 3. Marts Layer (Star Schema)
The final analytical layer is built using dbt. It follows a Kimball Star Schema design, optimized for BI tools and SQL analysis.

### Fact Table: Sales (`fact_sales`)
| Column | Type | Description |
| :--- | :--- | :--- |
| `transaction_id` | string | Unique hashing of date, customer, and product. |
| `date` | datetime | Standardized transaction date. |
| `net_amount` | decimal | `total_amount` - `discount_amount`. Primary revenue metric. |
| `unit_price` | decimal | Derived price per unit at sale time. |

### Dimension: Customers (`dim_customers`)
Contains cleaned and governed customer data.
| Column | Type | Description |
| :--- | :--- | :--- |
| `email_hash` | string | MD5 hash of customer email for join-ability without PII exposure. |
| `phone_preview` | string | Masked phone number (e.g., `***-***-1234`). |
| `masked_address` | string | Fully redacted street address. |
| `is_active` | boolean | Calculated flag based on 90-day purchase history. |

### Dimension: Products (`dim_products`)
| Column | Type | Description |
| :--- | :--- | :--- |
| `product_name` | string | Standardized name across all brands. |
| `brand_name` | string | Denormalized brand name for easier reporting. |
| `category` | string | Top-level product category. |
