SELECT 
    s.transaction_id,
    s.date,
    s.customer_id,
    s.product_id,
    s.store_id,
    CASE 
        -- Deterministically assign ~25% of transactions to online channels
        -- using a hash of the transaction_id to ensure reproducibility
        WHEN abs(hash(s.transaction_id)) % 100 < 25 THEN
            CASE abs(hash(s.transaction_id || '_ch')) % 4
                WHEN 0 THEN 'ONL-001'  -- Official Website
                WHEN 1 THEN 'ONL-002'  -- Mobile App
                WHEN 2 THEN 'ONL-003'  -- Tokopedia
                WHEN 3 THEN 'ONL-004'  -- Shopee
            END
        ELSE NULL  -- Offline/In-store transaction
    END as channel_id,
    s.promotion_id,
    s.units_sold,
    s.unit_price,
    s.total_amount,
    s.discount_amount,
    s.net_amount
FROM {{ ref('stg_sales') }} s
INNER JOIN {{ ref('stg_customers') }} c ON s.customer_id = c.customer_id
INNER JOIN {{ ref('stg_products') }} p ON s.product_id = p.product_id
LEFT JOIN {{ ref('stg_stores') }} st ON s.store_id = st.store_id
