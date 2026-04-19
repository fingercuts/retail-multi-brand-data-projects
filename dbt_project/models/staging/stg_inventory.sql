SELECT 
    store_id,
    product_id,
    COALESCE(stock_on_hand, 0) as stock_on_hand,
    COALESCE(reorder_level, 0) as reorder_level,
    COALESCE(
        TRY_CAST(last_restocked_date AS TIMESTAMP),
        TRY_CAST(last_restocked_date AS DATE),
        strptime(last_restocked_date::VARCHAR, '%m/%d/%Y'),
        strptime(last_restocked_date::VARCHAR, '%d/%m/%Y')
    ) as last_restocked_date
FROM {{ source('staging', 'raw_inventory') }}
WHERE store_id IS NOT NULL 
  AND product_id IS NOT NULL
  AND stock_on_hand >= 0
