SQL_TEMPLATE__CREATE_ATTRIBUTE = """
CREATE TABLE attr__{{ entity_name }}__{{ attribute_name }}(
    {{ entity_name }}_sk VARCHAR(32) NOT NULL,
    {{ attribute_name }} {{ attribute_type }},
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
