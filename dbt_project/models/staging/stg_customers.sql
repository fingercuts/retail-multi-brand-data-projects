SELECT 
    customer_id,
    {{ mask_pii('name', 'mask') }} as customer_name,
    gender,
    age,
    city,
    region,
    {{ mask_pii('email', 'hash') }} as email_hash,
    {{ mask_pii('phone_number', 'partial') }} as phone_preview,
    {{ mask_pii('street_address', 'mask') }} as masked_address
FROM {{ source('staging', 'raw_customers') }}
WHERE customer_id IS NOT NULL 
  AND age BETWEEN 1 AND 120
