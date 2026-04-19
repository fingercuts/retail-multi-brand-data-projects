{% snapshot sns_stores %}

{{
    config(
      target_schema='main',
      strategy='check',
      unique_key='store_id',
      check_cols=['status', 'region'],
    )
}}

select * from {{ ref('stg_stores') }}

{% endsnapshot %}
