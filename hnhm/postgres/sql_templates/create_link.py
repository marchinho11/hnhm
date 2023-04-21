SQL_TEMPLATE__CREATE_LINK = """
CREATE TABLE link__{{ name }}(
    {% for entity in entities -%}
        {{ entity }}_sk VARCHAR(32) NOT NULL,
    {% endfor -%}
    valid_from TIMESTAMPTZ NOT NULL,
    valid_to TIMESTAMPTZ,
    _source VARCHAR(512) NOT NULL,
    _loaded_at TIMESTAMPTZ NOT NULL,

    {% for entity in entities -%}
        CONSTRAINT fk_{{ entity }}_sk
            FOREIGN KEY({{ entity }}_sk) 
            REFERENCES hub__{{ entity }}({{ entity }}_sk)
            ON DELETE NO ACTION,
    {% endfor -%}

    PRIMARY KEY({{ primary_keys | join(', ') }})
)
"""
