BEGIN;

CREATE TABLE tmp__{{ target_table }}__load__new
AS
WITH data_all AS (
    SELECT
        {{ source_sk }} AS {{ target_sk }},
        {% for source_attribute, target_attribute in zip(source_attributes, target_attributes) -%}
            {{ source_attribute }} AS {{ target_attribute }},
        {% endfor -%}
        {{ business_time_field }} AS valid_from,
        MD5(CONCAT_WS('-',
            {% for source_attribute in source_attributes -%}
                COALESCE({{ source_attribute }}::TEXT, 'null') {% if not loop.last %}, {% endif %}
            {% endfor -%}
        )) AS _hash
    FROM
        {{ source_table }}
    UNION ALL
    SELECT
        {{ target_sk }},
        {{ target_attributes | join(",") }},
        valid_from,
        _hash
    FROM
        {{ target_table }}
),
data_unique AS (
    SELECT
        DISTINCT ON (
            {{ target_sk }}, _hash
        )
        {{ target_sk }},
        {{ target_attributes | join(",")}},
        valid_from,
        _hash
    FROM
        data_all
    ORDER BY
         {{ target_sk }}, _hash, valid_from DESC
),
data AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY {{ target_sk }}
            ORDER BY     valid_from
        ) AS row_number
    FROM
        data_unique
)
SELECT
    d1.{{ target_sk }},
    {% for target_attribute in target_attributes -%}
        d1.{{ target_attribute }},
    {% endfor -%}
    d1.valid_from,
    CASE
        WHEN d2.valid_from IS NULL THEN 'infinity'
        ELSE d2.valid_from
    END AS valid_to,
    d1._hash AS _hash,
    '{{ source_table }}' AS _source,
    CURRENT_TIMESTAMP AS _loaded_at
FROM
    data d1
LEFT JOIN
    data d2
    ON d1.row_number = d2.row_number - 1
    AND d1.{{ target_sk }} = d2.{{ target_sk }};


WITH inserts AS (
    SELECT
        tmp.{{ target_sk }},
        {% for target_attribute in target_attributes -%}
            tmp.{{ target_attribute }},
        {% endfor -%}
        tmp.valid_from,
        tmp.valid_to,
        tmp._hash,
        tmp._source,
        tmp._loaded_at
    FROM
        tmp__{{ target_table }}__load__new tmp
    LEFT OUTER JOIN
        {{ target_table }} t
        ON tmp.{{ target_sk }} = t.{{ target_sk }}
        AND tmp._hash = t._hash
    WHERE
        t.{{ target_sk }} IS NULL
)
INSERT INTO {{ target_table }}(
    {{ target_sk }},
    {{ target_attributes | join(",")}},
    valid_from,
    valid_to,
    _hash,
    _source,
    _loaded_at
)
SELECT
    {{ target_sks | join(', ') }},
    {{ target_attributes | join(",")}},
    valid_from,
    valid_to,
    _hash,
    _source,
    _loaded_at
FROM
    inserts;


UPDATE {{ target_table }} t
SET
    valid_from = tmp.valid_from,
    valid_to = tmp.valid_to,
    _source = tmp._source,
    _loaded_at = tmp._loaded_at
FROM
    tmp__{{ target_table }}__load__new tmp
WHERE
    tmp.{{ target_sk }} = t.{{ target_sk }}
    AND tmp._hash = t._hash;

DROP TABLE tmp__{{ target_table }}__load__new;

COMMIT;
