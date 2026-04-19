SELECT 
    promotion_id,
    promotion_name,
    campaign_type,
    discount_pct,
    start_date,
    end_date
FROM {{ ref('stg_promotions') }}
