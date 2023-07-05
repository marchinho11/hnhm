/*
Schema looks like:
- (sk_1, ..., sk_n, valid_from, valid_to)

Keys are:
- (sk_1, ..., sk_k) {k <= n}

For each:
- Unique combination (sk_1, ..., sk_k, valid_from) we should have a separate row
- Where valid_from = business_time_field
*/

BEGIN;

CREATE TABLE tmp__{{ target_table }}__load_link
AS
WITH data_all AS (
    SELECT
        {% for source_sk, target_sk in zip(source_sks, target_sks) -%}
            {{ source_sk }} AS {{ target_sk }},
        {% endfor -%}
        {{ business_time_field }} AS valid_from
    FROM
        {{ source_table }}
    UNION ALL
    SELECT
        {{ target_sks | join(",") }},
        valid_from
    FROM
        {{ target_table }}
),
data_unique AS (
    SELECT
        DISTINCT ON (
            {{ key_sks | join(",") }}, valid_from
        )
        {{ target_sks | join(",") }},
        valid_from
    FROM
        data_all
    ORDER BY
         {{ key_sks | join(",") }}, valid_from DESC
),
data AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY {{ key_sks | join(",") }}
            ORDER BY     valid_from
        ) AS row_number
    FROM
        data_unique
)
SELECT
    {% for target_sk in target_sks -%}
        d1.{{ target_sk }},
    {% endfor -%}
    d1.valid_from,
    CASE
        WHEN d2.valid_from IS NULL THEN 'infinity'
        ELSE d2.valid_from
    END AS valid_to,
    '{{ source_table }}' AS _source,
    CURRENT_TIMESTAMP AS _loaded_at
FROM
    data d1
LEFT JOIN
    data d2
    ON d1.row_number = d2.row_number - 1
    {% for key_sk in key_sks -%}
        AND d1.{{ key_sk }} = d2.{{ key_sk }}
    {% endfor -%};


WITH inserts AS (
    SELECT
        {% for target_sk in target_sks -%}
            tmp.{{ target_sk }},
        {% endfor -%}
        tmp.valid_from,
        tmp.valid_to,
        tmp._source,
        tmp._loaded_at
    FROM
        tmp__{{ target_table }}__load_link tmp
    LEFT OUTER JOIN
        {{ target_table }} t
        ON
            tmp.valid_from = t.valid_from
            {% for key_sk in key_sks -%}
                AND tmp.{{ key_sk }} = t.{{ key_sk }}
            {% endfor -%}
    WHERE
        t.{{ target_sks[0] }} IS NULL
)
INSERT INTO {{ target_table }}(
    {{ target_sks | join(",") }},
    valid_from,
    valid_to,
    _source,
    _loaded_at
)
SELECT
    {{ target_sks | join(",") }},
    valid_from,
    valid_to,
    _source,
    _loaded_at
FROM
    inserts;


UPDATE {{ target_table }} t
SET
    valid_to = tmp.valid_to,
    _source = tmp._source,
    _loaded_at = tmp._loaded_at
FROM
    tmp__{{ target_table }}__load_link tmp
WHERE
    tmp.valid_from = t.valid_from
    {% for key_sk in key_sks -%}
        AND tmp.{{ key_sk }} = t.{{ key_sk }}
    {% endfor -%};

DROP TABLE tmp__{{ target_table }}__load_link;

COMMIT;
