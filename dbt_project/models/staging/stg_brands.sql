SELECT 
    brand_id,
    brand_name,
    category
FROM {{ source('staging', 'raw_brands') }}
WHERE brand_id IS NOT NULL
