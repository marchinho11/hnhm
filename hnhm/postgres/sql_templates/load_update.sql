BEGIN;

CREATE TABLE tmp__{{ target_table }}__load__update
AS
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
    {{ source_table }};


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
    tmp__{{ target_table }}__load__update source_data
LEFT OUTER JOIN
    {{ target_table }} target_data
    ON source_data.sk = target_data.{{ target_sk }}
WHERE
    target_data.{{ target_sk }} IS NULL
    AND source_data.row_number = 1;


WITH updates AS (
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
        tmp__{{ target_table }}__load__update source_data
    INNER JOIN
        {{ target_table }} target_data
        ON source_data.sk = target_data.{{ target_sk }}
    WHERE
        source_data._hash != target_data._hash
        AND source_data.valid_from >= target_data.valid_from
)
UPDATE
    {{ target_table }}
SET
    {% for source_attribute, target_attribute in zip(source_attributes, target_attributes) -%}
        {{ target_attribute }} = updates.{{ source_attribute }},
    {% endfor -%}
    valid_from = updates.valid_from,
    _hash = updates._hash,
    _source = updates._source,
    _loaded_at = updates._loaded_at
FROM
    updates
WHERE
    {{ target_sk }} = updates.sk;

DROP TABLE tmp__{{ target_table }}__load__update;

COMMIT;
