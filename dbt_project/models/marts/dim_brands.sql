SELECT 
    brand_id,
    brand_name
FROM {{ ref('stg_brands') }}
