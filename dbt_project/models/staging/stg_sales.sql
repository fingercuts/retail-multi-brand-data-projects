WITH normalized_sales AS (
    SELECT 
        -- Generate a unique transaction ID since raw data lacks one
        md5(concat(date, store_id, product_id, customer_id)) as transaction_id,
        
        -- Robust date parsing to handle mixed formats
        COALESCE(
            TRY_CAST(date AS TIMESTAMP),
            TRY_CAST(date AS DATE),
            strptime(date::VARCHAR, '%m/%d/%Y %I:%M %p'),
            strptime(date::VARCHAR, '%m/%d/%Y'),
            strptime(date::VARCHAR, '%d/%m/%Y')
        ) as date,
        
        customer_id,
        product_id,
        store_id,
        promotion_id,
        COALESCE(units_sold, 0) as units_sold,
        total_amount,
        discounted_amount as discount_amount,
        (total_amount - discounted_amount) as net_amount,
        CASE 
            WHEN units_sold > 0 THEN (total_amount / units_sold) 
            ELSE 0 
        END as unit_price
    FROM {{ source('staging', 'raw_sales') }}
)

SELECT * FROM normalized_sales
WHERE units_sold > 0 
  AND date IS NOT NULL 
  AND total_amount >= 0 
  AND net_amount >= 0
