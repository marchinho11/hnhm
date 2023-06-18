from tests.util import get_views, get_tables, get_columns
from tests.__hnhm__ import (
    UserWith1Key,
    UserWith1Key1Group,
    UserWith1Key1Attribute,
    UserWith1Key1Attribute1Group,
    UserWith1Key1GroupExtraAttribute,
)


def test_hub_only(hnhm, cursor):
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWith1Key()]))

    assert get_tables(cursor) == {"hub__user"}
    assert get_views(cursor) == {"entity__user"}
    assert get_columns("hub__user", cursor) == {
        "user_sk",
        "user_id_bk",
        "valid_from",
        "_source",
        "_loaded_at",
    }

    with hnhm:
        hnhm.apply(hnhm.plan(entities=[]))
    assert not get_tables(cursor)
    assert not get_views(cursor)


def test_with_attribute(hnhm, cursor):
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWith1Key1Attribute()]))

    assert get_tables(cursor) == {"hub__user", "attr__user__age"}
    assert get_views(cursor) == {"entity__user"}
    assert get_columns("attr__user__age", cursor) == {
        "user_sk",
        "age",
        "valid_from",
        "_source",
        "_loaded_at",
    }

    with hnhm:
        hnhm.apply(hnhm.plan(entities=[]))
    assert not get_tables(cursor)
    assert not get_views(cursor)


def test_attribute__add_remove(hnhm, cursor):
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWith1Key()]))
    assert get_tables(cursor) == {"hub__user"}
    assert get_views(cursor) == {"entity__user"}

    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWith1Key1Attribute()]))
    assert get_tables(cursor) == {"hub__user", "attr__user__age"}

    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWith1Key()]))
    assert get_tables(cursor) == {"hub__user"}


def test_with_group(hnhm, cursor):
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWith1Key1Group()]))
    assert get_tables(cursor) == {"hub__user", "group__user__name"}
    assert get_views(cursor) == {"entity__user"}
    assert get_columns("group__user__name", cursor) == {
        "user_sk",
        "first_name",
        "last_name",
        "valid_from",
        "_source",
        "_loaded_at",
    }

    with hnhm:
        hnhm.apply(hnhm.plan(entities=[]))
    assert not get_tables(cursor)
    assert not get_views(cursor)


def test_group__add_remove(hnhm, cursor):
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWith1Key()]))
    assert get_tables(cursor) == {"hub__user"}
    assert get_views(cursor) == {"entity__user"}

    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWith1Key1Group()]))
    assert get_tables(cursor) == {"hub__user", "group__user__name"}

    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWith1Key()]))
    assert get_tables(cursor) == {"hub__user"}


def test_with_attribute_and_group(hnhm, cursor):
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWith1Key1Attribute1Group()]))
    assert get_tables(cursor) == {"hub__user", "attr__user__age", "group__user__name"}
    assert get_views(cursor) == {"entity__user"}

    with hnhm:
        hnhm.apply(hnhm.plan(entities=[]))
    assert not get_tables(cursor)
    assert not get_views(cursor)


def test_group__add_remove_attribute(hnhm, cursor):
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWith1Key1Group()]))
    assert get_tables(cursor) == {"hub__user", "group__user__name"}
    assert get_views(cursor) == {"entity__user"}
    assert get_columns("group__user__name", cursor) == {
        "user_sk",
        "first_name",
        "last_name",
        "valid_from",
        "_source",
        "_loaded_at",
    }

    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWith1Key1GroupExtraAttribute()]))
    assert get_tables(cursor) == {"hub__user", "group__user__name"}
    assert get_columns("group__user__name", cursor) == {
        "user_sk",
        "first_name",
        "last_name",
        "third_name",
        "valid_from",
        "_source",
        "_loaded_at",
    }

    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWith1Key1Group()]))
    assert get_tables(cursor) == {"hub__user", "group__user__name"}
    assert get_columns("group__user__name", cursor) == {
        "user_sk",
        "first_name",
        "last_name",
        "valid_from",
        "_source",
        "_loaded_at",
    }

    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWith1Key()]))
    assert get_tables(cursor) == {"hub__user"}
