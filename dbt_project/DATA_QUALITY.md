# Data Quality Framework

This project follows a "Security-First" and "Clean-Room" data processing philosophy. This document defines the cleansing logic and quality checks implemented at the staging and mart layers.

## 1. Core Cleansing Logic
The filtering logic in `models/staging/` ensures that analytical models are built only on physically valid data.

### Referential Integrity
- Records with `NULL` unique identifiers (e.g., `transaction_id`, `customer_id`) are systematically excluded at the staging boundary.
- Staging models are joined via `INNER JOIN` in the Marts layer to ensure that if a source record was dropped due to quality issues, its dependencies are not orphaned in the final reports.

### Physical Validity Controls
| Entity | Logic |
| :--- | :--- |
| **Sales** | Filters out `units_sold <= 0` and non-parsable dates. |
| **Finance** | Excludes negative `total_amount` or `net_amount` records. |
| **Demographics** | Filters for `age BETWEEN 1 AND 120`. |
| **Inventory** | Excludes negative `stock_on_hand`. |

---

## 2. PII Governance & Masking
To maintain GDPR/CCPA compliance, PII is never allowed to enter the analytical `fact_sales` or `dim_customers` tables in plain text.

- **Hashing**: Customer emails are transformed using `MD5` hashing for secure cross-brand joining.
- **Redaction**: Physical street addresses are 100% redacted at the staging level.
- **Partial Masking**: Sensitive identifiers like phone numbers are partially masked (showing only the last 4 digits).

---

## 3. dbt Testing Strategy
Automated tests are defined in `schema.yml` to prevent regression.

- **Primary Key Tests**: All `_id` columns are tested for uniqueness and non-null values.
- **Relational Integrity**: Foreign keys in `fact_sales` are validated against their respective dimensions.
- **Threshold Alerts**: Specific columns (like `units_sold`) have alert thresholds (e.g., 1-1,000 units) to flag potential data entry anomalies for human review.
