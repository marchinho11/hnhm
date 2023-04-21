SQL_TEMPLATE__CREATE_GROUP = """
CREATE TABLE group__{{ entity_name }}__{{ group_name }}(
    {{ entity_name }}_sk VARCHAR(32) NOT NULL,
    {% for column in columns -%}
        {{ column }},
    {% endfor -%}
    {% for time_column in time_columns -%}
        {{ time_column }},
    {% endfor -%}
    _source VARCHAR(512) NOT NULL,
    _loaded_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT fk_{{ entity_name }}_sk
        FOREIGN KEY({{ entity_name }}_sk) 
        REFERENCES hub__{{ entity_name }}({{ entity_name }}_sk)
        ON DELETE NO ACTION
)"""
