SQL_TEMPLATE__LOAD_HUB = """
INSERT INTO hub__{{ target_name }}(
    {{ target_name }}_sk,
    {% for target_key in target_keys -%}
        {{ target_key }}_bk,
    {% endfor -%}
    valid_from,
    _source,
    _loaded_at
)
SELECT
    {{ source_sk }},
    {% for source_key in source_keys -%}
        {{ source_key }},
    {% endfor -%}
    {{ business_time_field }},
    'stg__{{ source_name }}',
    CURRENT_TIMESTAMP
FROM
    stg__{{ source_name }}
ON CONFLICT
    ({{ target_name }}_sk) DO NOTHING
"""
