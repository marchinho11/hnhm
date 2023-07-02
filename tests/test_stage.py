import pytest

from hnhm import HnhmError
from tests.util import get_views, get_tables, get_columns
from tests.__hnhm__ import (
    StageNoColumns,
    StageWith1Column,
    StageWith5Columns,
    StageWith6Columns,
)


def test_plan_at_least_one_attribute(hnhm):
    with pytest.raises(
        HnhmError, match="Entity='STAGE.stage' should have at least 1 attribute."
    ), hnhm:
        hnhm.plan(entities=[StageNoColumns()])


def test_works(hnhm, cursor):
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[StageWith5Columns()]))

    assert get_tables(cursor) == {"stg__stage"}
    assert not get_views(cursor)

    with hnhm:
        hnhm.apply(hnhm.plan(entities=[]))
    assert not get_tables(cursor)


def test_add_attribute(hnhm, cursor):
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[StageWith5Columns()]))

    assert get_tables(cursor) == {"stg__stage"}
    assert get_columns("stg__stage", cursor) == {
        "user_id",
        "review_id",
        "name",
        "age",
        "time",
    }

    with hnhm:
        hnhm.apply(hnhm.plan(entities=[StageWith6Columns()]))

    assert get_columns("stg__stage", cursor) == {
        "user_id",
        "review_id",
        "name",
        "age",
        "time",
        "new_id",
    }


def test_remove_attribute(hnhm, cursor):
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[StageWith5Columns()]))

    assert get_tables(cursor) == {"stg__stage"}
    assert get_columns("stg__stage", cursor) == {
        "user_id",
        "review_id",
        "name",
        "age",
        "time",
    }

    with hnhm:
        hnhm.apply(hnhm.plan(entities=[StageWith1Column()]))
    assert get_columns("stg__stage", cursor) == {"user_id"}


def test_try_remove_all_columns(hnhm):
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[StageWith5Columns()]))

    with pytest.raises(
        HnhmError, match="Entity='STAGE.stage' should have at least 1 attribute."
    ), hnhm:
        hnhm.apply(hnhm.plan(entities=[StageNoColumns()]))
