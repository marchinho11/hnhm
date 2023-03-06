SQL_TEMPLATE__CREATE_STAGE = """
CREATE TABLE stg__{{ name }}(
    {% for column, column_type in zip(columns, columns_types) -%}
        {{ column }} {{ column_type }} {% if not loop.last %} , {% endif %}
    {% endfor -%}
)"""
