from tests.dwh import User, Review, UserReview
from tests.util import get_tables_in_database, get_column_names_for_table


def test_link(hnhm, sqlalchemy_engine):
    # Create
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[User(), Review()], links=[UserReview()]))
    assert get_tables_in_database(sqlalchemy_engine) == {
        "hub__user",
        "hub__review",
        "link__user_review",
    }
    assert get_column_names_for_table(sqlalchemy_engine, "link__user_review") == {
        "user_sk",
        "review_sk",
        "valid_from",
        "valid_to",
        "_source",
        "_loaded_at",
    }

    # Cleanup
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[], links=[]))
    assert not get_tables_in_database(sqlalchemy_engine)
