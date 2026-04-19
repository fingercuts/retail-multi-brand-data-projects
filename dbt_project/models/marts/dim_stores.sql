SELECT 
    store_id,
    store_name,
    brand_id,
    city,
    region,
    subsidiary_company,
    channel as store_type,
    opening_year,
    status
FROM {{ ref('stg_stores') }}
