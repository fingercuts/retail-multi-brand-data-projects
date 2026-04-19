SELECT 
    s.transaction_id,
    s.date,
    s.customer_id,
    s.product_id,
    s.store_id,
    CASE 
        -- 1. Check if the transaction explicitly uses an Online store ID or marker
        WHEN s.store_id ILIKE 'ONL%' OR s.store_id ILIKE '%ONLINE%' THEN 'ONL-001'
        
        -- 2. Detect platform from the joined store name (if it exist)
        WHEN st.store_name ILIKE '%Website%' THEN 'ONL-001'
        WHEN st.store_name ILIKE '%App%' THEN 'ONL-002'
        WHEN st.store_name ILIKE '%Tokopedia%' THEN 'ONL-003'
        WHEN st.store_name ILIKE '%Shopee%' THEN 'ONL-004'
        
        -- 3. If the store dimension explicitly lists it as Online
        WHEN st.channel = 'Online' THEN COALESCE(ch.channel_id, 'ONL-001')
        
        -- 4. Catch transactions with no matching store (Unmapped/Digital)
        WHEN st.store_id IS NULL OR st.store_id = '' THEN 'ONL-001'
        
        -- 5. Explicitly Offline stores
        WHEN st.channel = 'Offline' THEN NULL 
        
        -- 6. Default fallback for everything else
        ELSE 'ONL-001' 
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
LEFT JOIN {{ ref('stg_channels') }} ch 
    ON st.channel = ch.channel_name 
    OR st.channel = ch.type 
    OR (st.channel = 'Online' AND ch.channel_id = 'ONL-001')
