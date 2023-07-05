WITH source_data AS (
    SELECT
        {{ source_sk }} AS sk,
        {{ business_time_field }} AS valid_from,
        '{{ source_table }}' AS _source,
        CURRENT_TIMESTAMP AS _loaded_at,
        {{ source_attributes | join(",") }},

        MD5(CONCAT_WS('-',
            {% for source_attribute in source_attributes -%}
                COALESCE({{ source_attribute }}::TEXT, 'null') {% if not loop.last %}, {% endif %}
            {% endfor -%}
        )) AS _hash,

        ROW_NUMBER() OVER (
            PARTITION BY {{ source_sk }}
            ORDER BY     {{ business_time_field }} DESC
        ) AS row_number
    FROM
        {{ source_table }}
)
INSERT INTO {{ target_table }}(
    {{ target_sk }},
    {{ target_attributes | join(",") }},
    valid_from,
    _hash,
    _source,
    _loaded_at
)
SELECT
    source_data.sk,
    {% for source_attribute in source_attributes -%}
        source_data.{{ source_attribute }},
    {% endfor -%}
    source_data.valid_from,
    source_data._hash,
    source_data._source,
    source_data._loaded_at
FROM
    source_data
LEFT OUTER JOIN
    {{ target_table }} target_data
    ON source_data.sk = target_data.{{ target_sk }}
WHERE
    target_data.{{ target_sk }} IS NULL
    AND source_data.row_number = 1
