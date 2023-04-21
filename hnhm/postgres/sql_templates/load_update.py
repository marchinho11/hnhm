SQL_TEMPLATE__LOAD_UPDATE = """
BEGIN;

CREATE TABLE tmp__{{ target_table }}__load__update
AS
SELECT
    {{ source_sk }} AS sk,
    {{ business_time_field }} AS valid_from,

    {% for source_attribute in source_attributes -%}
        {{ source_attribute }},
    {% endfor -%}

    ROW_NUMBER() OVER (
        PARTITION BY {{ source_sk }}
        ORDER BY     {{ business_time_field }} DESC
    ) AS row_number,
    '{{ source_table }}' AS _source,
    CURRENT_TIMESTAMP AS _loaded_at 
FROM
    {{ source_table }};


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
    d._source,
    d._loaded_at
FROM
    tmp__{{ target_table }}__load__update d
LEFT OUTER JOIN
    {{ target_table }} t
    ON d.sk = t.{{ target_sk }}
WHERE
    t.{{ target_sk }} IS NULL
    AND d.row_number = 1;


WITH updates AS (
    SELECT
        d.sk,
        {% for source_attribute in source_attributes -%}
            d.{{ source_attribute }},
        {% endfor -%}
        d.valid_from,
        d._source,
        d._loaded_at
    FROM
        tmp__{{ target_table }}__load__update d
    INNER JOIN
        {{ target_table }} t
        ON d.sk = t.{{ target_sk }}
    WHERE
        {% for source_attribute, target_attribute in zip(source_attributes, target_attributes) -%}
            d.{{ source_attribute }} != t.{{ target_attribute }}
            {% if not loop.last %} AND {% endif %}
        {% endfor -%}
        AND d.valid_from >= t.valid_from
)
UPDATE
    {{ target_table }}
SET
    {% for source_attribute, target_attribute in zip(source_attributes, target_attributes) -%}
        {{ target_attribute }} = u.{{ source_attribute }},
    {% endfor -%}
    valid_from = u.valid_from,
    _source = u._source,
    _loaded_at = u._loaded_at
FROM
    updates u
WHERE
    {{ target_sk }} = u.sk;

DROP TABLE tmp__{{ target_table }}__load__update;

COMMIT;
"""
