CREATE TABLE attr__{{ entity_name }}__{{ attribute_name }}(
    {{ entity_name }}_sk VARCHAR(32) NOT NULL,
    {{ attribute_name }} {{ attribute_type }},
    valid_from TIMESTAMPTZ NOT NULL,
    {% if is_scd2 %}
        valid_to TIMESTAMPTZ,
    {% endif %}
    _hash VARCHAR(32) NOT NULL,
    _source VARCHAR(512) NOT NULL,
    _loaded_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT fk_{{ entity_name }}_sk
      FOREIGN KEY({{ entity_name }}_sk) 
        REFERENCES hub__{{ entity_name }}({{ entity_name }}_sk)
        ON DELETE NO ACTION
)
