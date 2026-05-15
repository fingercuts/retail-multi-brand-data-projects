SELECT 
    customer_id,
    {{ mask_pii('name', 'mask') }} as customer_name,
    CASE 
        WHEN UPPER(TRIM(gender)) IN ('M', 'MALE') THEN 'Male'
        WHEN UPPER(TRIM(gender)) IN ('F', 'FEMALE') THEN 'Female'
        ELSE 'Not Specified'
    END AS gender,
    age,
    CONCAT(UPPER(SUBSTR(TRIM(city), 1, 1)), LOWER(SUBSTR(TRIM(city), 2))) AS city,
    TRIM(region) AS region,
    {{ mask_pii('email', 'hash') }} as email_hash,
    {{ mask_pii('phone_number', 'partial') }} as phone_preview,
    {{ mask_pii('street_address', 'mask') }} as masked_address
FROM {{ source('staging', 'raw_customers') }}
WHERE customer_id IS NOT NULL 
  AND age BETWEEN 1 AND 120
