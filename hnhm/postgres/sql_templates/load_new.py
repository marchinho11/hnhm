SQL_TEMPLATE__LOAD_NEW = """
BEGIN;

CREATE TABLE _tmp__{{ target_table }}__load__new
AS
WITH data_all AS (
    SELECT
        {% for source_sk, target_sk in zip(source_sks, target_sks) -%}
            {{ source_sk }} AS {{ target_sk }},
        {% endfor -%}

        {% for source_attribute, target_attribute in zip(source_attributes, target_attributes) -%}
            {{ source_attribute }} AS {{ target_attribute }},
        {% endfor -%}

        {{ business_time_field }} AS valid_from
    FROM
        {{ source_table }}
    UNION ALL
    SELECT
        {% for target_sk in target_sks -%}
            {{ target_sk }},
        {% endfor -%}

        {% for target_attribute in target_attributes -%}
            {{ target_attribute }},
        {% endfor -%}

        valid_from
    FROM
        {{ target_table }}
),
data_unique AS (
    SELECT
        DISTINCT ON (
            {{ (target_sks+target_attributes+extra_sks) | join(', ') }}
        )

        {% for target_sk in target_sks -%}
            {{ target_sk }},
        {% endfor -%}

        {% for target_attribute in target_attributes -%}
            {{ target_attribute }},
        {% endfor -%}

        valid_from
    FROM
        data_all
    ORDER BY
         {{ (target_sks+target_attributes) | join(', ') }}, valid_from DESC
),
data AS (
    SELECT
        {{ target_sks | join(', ') }},
        {% for target_attribute in target_attributes -%}
            {{ target_attribute }},
        {% endfor -%}
        valid_from,
        ROW_NUMBER() OVER (
            PARTITION BY {{ target_sks | join(', ') }}
            ORDER BY     valid_from
        ) AS row_number
    FROM
        data_unique
)
SELECT
    {% for target_sk in target_sks -%}
        d1.{{ target_sk }},
    {% endfor -%}

    {% for target_attribute in target_attributes -%}
        d1.{{ target_attribute }},
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

    {% for target_sk in target_sks -%}
        AND d1.{{ target_sk }} = d2.{{ target_sk }}
    {% endfor -%};


WITH inserts AS (
    SELECT
        {% for target_sk in target_sks -%}
            tmp.{{ target_sk }},
        {% endfor -%}

        {% for target_attribute in target_attributes -%}
            tmp.{{ target_attribute }},
        {% endfor -%}

        tmp.valid_from,
        tmp.valid_to,
        tmp._source,
        tmp._loaded_at
    FROM
        _tmp__{{ target_table }}__load__new tmp
    LEFT OUTER JOIN
        {{ target_table }} t
        ON (
            {% for where_element in (target_sks+target_attributes+extra_sks) -%}
                COALESCE(t.{{ where_element }}::TEXT, 'null')
                {% if not loop.last %} || '-' || {% endif %}
            {% endfor -%}
        ) = (
            {% for where_element in (target_sks+target_attributes+extra_sks) -%}
                COALESCE(tmp.{{ where_element }}::TEXT, 'null')
                {% if not loop.last %} || '-' || {% endif %}
            {% endfor -%}
        )
    WHERE
        {% for target_sk in (target_sks+extra_sks) -%}
            t.{{ target_sk }} IS NULL
            {% if not loop.last %} AND {% endif %}
        {% endfor -%}
)
INSERT INTO {{ target_table }}(
    {{ target_sks | join(', ') }},
    {% for target_attribute in target_attributes -%}
        {{ target_attribute }},
    {% endfor -%}
    valid_from,
    valid_to,
    _source,
    _loaded_at
)
SELECT
    {{ target_sks | join(', ') }},
    {% for target_attribute in target_attributes -%}
        {{ target_attribute }},
    {% endfor -%}
    valid_from,
    valid_to,
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
    _tmp__{{ target_table }}__load__new tmp
WHERE
    (
        {% for where_element in (target_sks+target_attributes+extra_sks) -%}
            COALESCE(t.{{ where_element }}::TEXT, 'null')
            {% if not loop.last %} || '-' || {% endif %}
        {% endfor -%}
    ) = (
        {% for where_element in (target_sks+target_attributes+extra_sks) -%}
            COALESCE(tmp.{{ where_element }}::TEXT, 'null')
            {% if not loop.last %} || '-' || {% endif %}
        {% endfor -%}
    );

DROP TABLE _tmp__{{ target_table }}__load__new;

COMMIT;
"""
