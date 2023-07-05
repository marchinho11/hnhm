CREATE TABLE stg__{{ name }}(
    {% for column, column_type in columns_with_types -%}
        {{ column }} {{ column_type }} {% if not loop.last %} , {% endif %}
    {% endfor -%}
)
