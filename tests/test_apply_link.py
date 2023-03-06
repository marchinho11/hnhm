from tests.util import get_tables_in_database
from tests.dwh import User, Review, UserReview


def test_create(hnhm, sqlalchemy_engine):
    # Create
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[User(), Review()], links=[UserReview()]))
    assert get_tables_in_database(sqlalchemy_engine) == {
        "hub__user",
        "hub__review",
        "link__user_review",
    }

    # Cleanup
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[], links=[]))
    assert not get_tables_in_database(sqlalchemy_engine)
