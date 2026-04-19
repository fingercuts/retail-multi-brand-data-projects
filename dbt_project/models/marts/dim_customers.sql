-- This is the "General Audience" version of the customer table.
-- It is masked to ensure GDPR/CCPA compliance for Analysts and BI tools.

SELECT 
    customer_id,
    customer_name, -- Masked via stg_customers macro
    gender,
    age,
    city,
    region,
    email_hash, -- Hashed: joinable but secure
    phone_preview, -- Partial mask: shows patterns but hides identity
    masked_address -- Fully masked
FROM {{ ref('stg_customers') }}
