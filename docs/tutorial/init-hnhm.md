# Init hNhM
Create the `__hnhm__.py` file with the following contents:
```python
# __hnhm__.py
from hnhm import PostgresPsycopgSql

sql = PostgresPsycopgSql(
    database="coinmarket",
    user="hnhm",
    password="123", # replace it with an environment variable in the future :)
    port=5433,
)
```

This `sql` object will help us to generate and execute SQL queries in the database.
