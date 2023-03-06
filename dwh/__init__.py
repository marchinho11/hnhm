from hnhm import HnHm, FileStorage, HnhmRegistry, PostgresSqlalchemySql

from .user import User
from .review import Review
from .amazon_stage import AmazonStg
from .user_review import LinkUserReview

__registry__ = HnhmRegistry(
    entities=[
        AmazonStg(),
        User(),
        Review(),
    ],
    links=[
        LinkUserReview(),
    ],
    hnhm=HnHm(
        storage=FileStorage("state.json"),
        sql=PostgresSqlalchemySql(database="hnhm", user="mark"),
    ),
)
