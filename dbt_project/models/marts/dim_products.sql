SELECT 
    p.product_id,
    p.product_name,
    p.category,
    p.brand_id,
    b.brand_name,
    p.price
FROM {{ ref('stg_products') }} p
LEFT JOIN {{ ref('dim_brands') }} b ON p.brand_id = b.brand_id
