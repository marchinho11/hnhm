from dwh.hnhm__listing import Listing
from dwh.stage__listing import ListingStage
from hnhm import HnHm, FileState, HnhmRegistry, PostgresPsycopgSql

sql = PostgresPsycopgSql(database="coinmarket", user="hnhm")

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
