SELECT 
    product_id,
    product_name,
    category,
    brand_id,
    CAST(price AS DOUBLE) as price
FROM {{ source('staging', 'raw_products') }}
WHERE product_id IS NOT NULL 
  AND price >= 0
