SELECT 
    channel_id,
    channel_name,
    type
FROM {{ source('staging', 'raw_channels') }}
WHERE channel_id IS NOT NULL
