{% snapshot sns_products %}

{{
    config(
      target_schema='main',
      strategy='check',
      unique_key='product_id',
      check_cols=['price', 'product_name'],
    )
}}

select * from {{ ref('stg_products') }}

{% endsnapshot %}
