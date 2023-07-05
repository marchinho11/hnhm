CREATE TABLE hub__{{ name }}(
    {{ name }}_sk VARCHAR(32) PRIMARY KEY,
    {% for column, column_type in columns_with_types -%}
        {{ column }}_bk {{ column_type }},
    {% endfor -%}
    valid_from TIMESTAMPTZ NOT NULL,
    _source VARCHAR(512) NOT NULL,
    _loaded_at TIMESTAMPTZ NOT NULL
)
