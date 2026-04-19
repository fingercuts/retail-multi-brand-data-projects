-- This represents the "Restricted" view that only a few people (like Admins or Support) can see.
-- In production, we would use dbt 'tags' or database 'grants' to control who can select from here.

SELECT 
    customer_id,
    name as raw_customer_name, -- Unmasked for authorized use
    email as raw_customer_email, -- Unmasked for authorized use
    phone_number as raw_phone_number,
    street_address,
    gender,
    age,
    city,
    region
FROM {{ source('staging', 'raw_customers') }}
