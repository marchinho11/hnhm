SQL_TEMPLATE__LOAD_IGNORE = """
WITH data AS (
    SELECT
        {{ source_sk }} AS sk,
        {{ business_time_field }} AS valid_from,

        {% for source_attribute in source_attributes -%}
            {{ source_attribute }},
        {% endfor -%}

        ROW_NUMBER() OVER (
            PARTITION BY {{ source_sk }}
            ORDER BY     {{ business_time_field }} DESC
        ) AS row_number
    FROM
        {{ source_table }}
)
INSERT INTO {{ target_table }}(
    {{ target_sk }},
    {% for target_attribute in target_attributes -%}
    {{ target_attribute }},
    {% endfor -%}
    valid_from,
    _source,
    _loaded_at
)
SELECT
    d.sk,
    {% for source_attribute in source_attributes -%}
        d.{{ source_attribute }},
    {% endfor -%}
    d.valid_from,
    '{{ source_table }}',
    CURRENT_TIMESTAMP
FROM
    data d
LEFT OUTER JOIN
    {{ target_table }} t
    ON d.sk = t.{{ target_sk }}
WHERE
    t.{{ target_sk }} IS NULL
    AND d.row_number = 1;
"""
