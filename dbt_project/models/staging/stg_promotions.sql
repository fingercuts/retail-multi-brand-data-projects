SELECT 
    promotion_id,
    promotion_name,
    campaign_type,
    COALESCE(discount_percentage, 0) as discount_pct,
    COALESCE(
        TRY_CAST(start_date AS TIMESTAMP),
        TRY_CAST(start_date AS DATE),
        strptime(start_date::VARCHAR, '%m/%d/%Y')
    ) as start_date,
    COALESCE(
        TRY_CAST(end_date AS TIMESTAMP),
        TRY_CAST(end_date AS DATE),
        strptime(end_date::VARCHAR, '%m/%d/%Y')
    ) as end_date
FROM {{ source('staging', 'raw_promotions') }}
WHERE promotion_id IS NOT NULL 
  AND discount_pct >= 0
  AND start_date IS NOT NULL
