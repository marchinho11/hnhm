from dwh.user import User
from hnhm import HnHm, FileState, HnhmRegistry, PostgresPsycopgSql

sql = PostgresPsycopgSql(database="hnhm", user="hnhm", password="123", port=5433)

registry = HnhmRegistry(
    entities=[User()],
    hnhm=HnHm(
        sql=sql,
        state=FileState("state.json"),
    ),
)
