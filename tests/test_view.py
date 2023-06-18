import pytest

from hnhm import HnhmError
from tests.util import get_views, get_columns
from tests.__hnhm__ import (
    UserWith1Key,
    UserWith1Key1Group,
    UserWith1Key1Attribute,
    UserWith1Key1Attribute1Group,
)


def test_only_sk(hnhm, cursor):
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWith1Key()]))
    assert get_views(cursor) == {"entity__user"}
    assert get_columns("entity__user", cursor) == {"user_sk"}

    with hnhm:
        hnhm.apply(hnhm.plan(entities=[]))
    assert not get_views(cursor)


def test_with_attribute(hnhm, cursor):
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWith1Key1Attribute()]))
    assert get_views(cursor) == {"entity__user"}
    assert get_columns("entity__user", cursor) == {"user_sk", "age"}


def test_with_group(hnhm, cursor):
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWith1Key1Group()]))
    assert get_views(cursor) == {"entity__user"}
    assert get_columns("entity__user", cursor) == {
        "name__last_name",
        "user_sk",
        "name__first_name",
    }


def test_with_group_and_attribute(hnhm, cursor):
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWith1Key1Attribute1Group()]))
    assert get_views(cursor) == {"entity__user"}
    assert get_columns("entity__user", cursor) == {
        "name__first_name",
        "age",
        "name__last_name",
        "user_sk",
    }


def test_fail_on_second_delete(hnhm, cursor):
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWith1Key()]))

    with hnhm:
        plan = hnhm.plan(entities=[])
        hnhm.apply(plan)

    with pytest.raises(HnhmError, match="Entity's View 'HNHM.user' doesn't exist."), hnhm:
        with hnhm:
            hnhm.apply(plan)


def test_remove_groups_attributes(hnhm, cursor):
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWith1Key1Attribute1Group()]))
    assert get_views(cursor) == {"entity__user"}
    assert get_columns("entity__user", cursor) == {
        "name__last_name",
        "user_sk",
        "name__first_name",
        "age",
    }

    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWith1Key1Group()]))
    assert get_columns("entity__user", cursor) == {
        "name__last_name",
        "user_sk",
        "name__first_name",
    }

    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWith1Key()]))
    assert get_columns("entity__user", cursor) == {"user_sk"}
