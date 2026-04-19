{% macro mask_pii(column_name, strategy='mask') %}
    
    {% if strategy == 'mask' %}
        -- Standard Masking: Replaces everything with asterisks
        '****'
    {% elif strategy == 'partial' %}
        -- Partial Masking: Shows only last 4 characters (good for phones)
        '***-***-' || RIGHT({{ column_name }}, 4)
    {% elif strategy == 'hash' %}
        -- Hashing: For joinable but anonymous identifiers (emails)
        md5({{ column_name }})
    {% else %}
        {{ column_name }}
    {% endif %}

{% endmacro %}
