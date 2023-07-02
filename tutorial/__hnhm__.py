from tutorial.hnhm__listing import Listing
from tutorial.stage__listing import ListingStage
from hnhm import HnHm, FileState, HnhmRegistry, PostgresPsycopgSql

sql = PostgresPsycopgSql(
    database="coinmarket",
    user="hnhm",
    password="123",
    port=5433,
)

registry = HnhmRegistry(
    entities=[
        ListingStage(),
        Listing(),
    ],
    hnhm=HnHm(
        state=FileState("coinmarket.json"),
        sql=sql,
    ),
)
