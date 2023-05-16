CREATE OR REPLACE VIEW {{ view_name }}
AS
SELECT
    {{ hub }}.{{ sk }} {%- if selects %}, {%- endif %}
    {% for table, column, alias in selects %}
        {{ table }}.{{ column }} AS {{ alias }}
        {%- if not loop.last %}, {%- endif %}
    {%- endfor %}
FROM
    {{ hub }}
{% for attribute in attributes -%}
LEFT JOIN
    {{ attribute.table }}
    ON {{ hub }}.{{ sk }} = {{ attribute.table }}.{{ sk }}
    {% if attribute.change_type == 'NEW' -%}
        AND {{ attribute.table }}.valid_to = 'infinity'
    {%- endif %}
{%- endfor %}
{% for group in groups -%}
LEFT JOIN
    {{ group.table }}
    ON {{ hub }}.{{ sk }} = {{ group.table }}.{{ sk }}
    {% if group.change_type == 'NEW' -%}
        AND {{ group.table }}.valid_to = 'infinity'
    {%- endif %}
{%- endfor %}
