# Data Governance & Privacy Framework

This document outlines the controls implemented in the Retail Multi-Brand Platform to manage PII (Personally Identifiable Information) and ensure analytical utility without compromising data privacy.

## PII Masking Strategy
The project uses a custom dbt macro, `mask_pii`, to standardize how sensitive fields are handled at the staging layer.

| Category | Field(s) | Implementation | Rationale |
| :--- | :--- | :--- | :--- |
| **Identifiability** | Name, Address | Full Redaction (`****`) | Not required for aggregate analytical trends. |
| **Connectivity** | Email | Deterministic Hashing (MD5) | Allows "blind joins" between datasets (e.g., Sales to Customer Loyalty) while preventing identity exposure. |
| **Contextual** | Phone | Partial Masking (`***-***-1234`) | Preserves regional area codes for geographic analysis while protecting specific numbers. |

## Access Control Layers
To support different business functions, we maintain a dual-layer view of the customer dimension:

### 1. Analytical View (`dim_customers`)
- **Audience**: BI dashboards, data analysts, marketing specialists.
- **Exposure**: Contains only masked and hashed values.
- **Utility**: Suitable for large-scale cohort analysis and metric calculation.

### 2. Operational/Admin View (`dim_customers_authorized`)
- **Audience**: Customer support admins, legal, system administrators.
- **Exposure**: Unmasked, raw transactional data.
- **Utility**: Used strictly for "right-to-be-forgotten" requests (GDPR) or resolving individual order discrepancies.

## Quality & lineage
Governance is integrated into the pipeline flow:
1.  **Ingestion Validation**: Pydantic models flag invalid schema types at the border.
2.  **Staging Cleanse**: dbt models apply masking macros immediately upon entry to the SQL warehouse.
3.  **Audit Logs**: Airflow logs capture the transformation lineage, ensuring we can trace every column back to its raw source for audit purposes.
