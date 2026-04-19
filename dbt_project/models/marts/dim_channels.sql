SELECT 
    channel_id,
    channel_name,
    type as channel_type
FROM {{ ref('stg_channels') }}
