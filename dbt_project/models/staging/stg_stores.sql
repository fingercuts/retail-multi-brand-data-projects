SELECT 
    store_id,
    store_name,
    brand_id,
    city,
    region,
    subsidiary_company,
    channel,
    opening_year,
    status
FROM {{ source('staging', 'raw_stores') }}
WHERE store_id IS NOT NULL
