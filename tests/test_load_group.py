from datetime import timedelta

from hnhm import Flow, String, Integer, ChangeType
from tests.__hnhm__ import UserWith1Key, StageWith5Columns
from tests.util import TIME, TIME_INFINITY, md5, get_rows, init_dwh, insert_row


class GroupIgnore(UserWith1Key):
    """Group Ignore."""

    name = String("User name", change_type=ChangeType.IGNORE, group="user_data")
    age = Integer("User age", change_type=ChangeType.IGNORE, group="user_data")


def test_ignore(hnhm, cursor):
    init_dwh(
        hnhm=hnhm,
        entities=[StageWith5Columns(), GroupIgnore()],
        stage_data={
            "stg__stage": [
                {
                    "user_id": "0",
                    "name": "Mark",
                    "age": 100,
                    "time": TIME,
                }
            ]
        },
        cursor=cursor,
    )
    expected = [
        {
            "user_sk": md5("0"),
            "name": "Mark",
            "age": 100,
            "valid_from": TIME,
            "_source": "stg__stage",
            "_hash": md5("Mark-100"),
        }
    ]

    flow = Flow(
        source=StageWith5Columns(), business_time_field=StageWith5Columns.time
    ).load(
        GroupIgnore(),
        mapping={
            GroupIgnore.user_id: StageWith5Columns.user_id,
            GroupIgnore.name: StageWith5Columns.name,
            GroupIgnore.age: StageWith5Columns.age,
        },
    )
    flow.execute(hnhm.sql)

    assert len(flow.tasks) == 2
    assert get_rows("group__user__user_data", cursor) == expected

    # Add new data
    insert_row(
        "stg__stage",
        {
            "user_id": "0",
            "name": "John",
            "age": 23,
            "time": TIME + timedelta(hours=1),
        },
        cursor,
    )

    flow.execute(hnhm.sql)

    assert len(flow.tasks) == 2
    assert get_rows("group__user__user_data", cursor) == expected


class GroupUpdate(UserWith1Key):
    """Group Update."""

    name = String("User name", change_type=ChangeType.UPDATE, group="user_data")
    age = Integer("User age", change_type=ChangeType.UPDATE, group="user_data")


def test_update(hnhm, cursor):
    init_dwh(
        hnhm=hnhm,
        entities=[StageWith5Columns(), GroupUpdate()],
        stage_data={
            "stg__stage": [
                {
                    "user_id": "0",
                    "name": "Mark",
                    "age": 100,
                    "time": TIME,
                }
            ]
        },
        cursor=cursor,
    )

    flow = Flow(
        source=StageWith5Columns(), business_time_field=StageWith5Columns.time
    ).load(
        GroupUpdate(),
        mapping={
            GroupUpdate.user_id: StageWith5Columns.user_id,
            GroupUpdate.name: StageWith5Columns.name,
            GroupUpdate.age: StageWith5Columns.age,
        },
    )
    flow.execute(hnhm.sql)

    assert len(flow.tasks) == 2
    assert get_rows("group__user__user_data", cursor) == [
        {
            "user_sk": md5("0"),
            "name": "Mark",
            "age": 100,
            "valid_from": TIME,
            "_source": "stg__stage",
            "_hash": md5("Mark-100"),
        }
    ]

    # Add new data
    insert_row(
        "stg__stage",
        {
            "user_id": "0",
            "name": "John",
            "age": 23,
            "time": TIME + timedelta(hours=1),
        },
        cursor,
    )

    flow.execute(hnhm.sql)

    assert len(flow.tasks) == 2
    assert get_rows("group__user__user_data", cursor) == [
        {
            "user_sk": md5("0"),
            "name": "John",
            "age": 23,
            "valid_from": TIME + timedelta(hours=1),
            "_source": "stg__stage",
            "_hash": md5("John-23"),
        }
    ]


class GroupNew(UserWith1Key):
    """Group New."""

    name = String("User name", change_type=ChangeType.NEW, group="user_data")
    age = Integer("User age", change_type=ChangeType.NEW, group="user_data")


def test_new(hnhm, cursor):
    init_dwh(
        hnhm=hnhm,
        entities=[StageWith5Columns(), GroupNew()],
        stage_data={
            "stg__stage": [
                {
                    "user_id": "0",
                    "name": "Mark",
                    "age": 100,
                    "time": TIME,
                }
            ]
        },
        cursor=cursor,
    )

    flow = Flow(
        source=StageWith5Columns(), business_time_field=StageWith5Columns.time
    ).load(
        GroupNew(),
        mapping={
            GroupNew.user_id: StageWith5Columns.user_id,
            GroupNew.name: StageWith5Columns.name,
            GroupNew.age: StageWith5Columns.age,
        },
    )
    flow.execute(hnhm.sql)

    assert len(flow.tasks) == 2
    assert get_rows("group__user__user_data", cursor) == [
        {
            "user_sk": md5("0"),
            "name": "Mark",
            "age": 100,
            "valid_from": TIME,
            "valid_to": TIME_INFINITY,
            "_source": "stg__stage",
            "_hash": md5("Mark-100"),
        }
    ]

    # Add new data
    insert_row(
        "stg__stage",
        {
            "user_id": "0",
            "name": "John",
            "age": 23,
            "time": TIME + timedelta(hours=1),
        },
        cursor,
    )
    flow.execute(hnhm.sql)
    assert get_rows("group__user__user_data", cursor, order_by="valid_from") == [
        {
            "user_sk": md5("0"),
            "name": "Mark",
            "age": 100,
            "valid_from": TIME,
            "valid_to": TIME + timedelta(hours=1),
            "_source": "stg__stage",
            "_hash": md5("Mark-100"),
        },
        {
            "user_sk": md5("0"),
            "name": "John",
            "age": 23,
            "valid_from": TIME + timedelta(hours=1),
            "valid_to": TIME_INFINITY,
            "_source": "stg__stage",
            "_hash": md5("John-23"),
        },
    ]

    # Insert in the middle
    insert_row(
        "stg__stage",
        {
            "user_id": "0",
            "name": "Jack",
            "age": None,
            "time": TIME + timedelta(minutes=30),
        },
        cursor,
    )
    # Duplicate
    insert_row(
        "stg__stage",
        {
            "user_id": "0",
            "name": "Jack",
            "age": None,
            "time": TIME + timedelta(minutes=30),
        },
        cursor,
    )
    flow.execute(hnhm.sql)

    assert get_rows("group__user__user_data", cursor, order_by="valid_from") == [
        {
            "user_sk": md5("0"),
            "name": "Mark",
            "age": 100,
            "valid_from": TIME,
            "valid_to": TIME + timedelta(minutes=30),
            "_source": "stg__stage",
            "_hash": md5("Mark-100"),
        },
        {
            "user_sk": md5("0"),
            "name": "Jack",
            "age": None,
            "valid_from": TIME + timedelta(minutes=30),
            "valid_to": TIME + timedelta(hours=1),
            "_source": "stg__stage",
            "_hash": md5("Jack-null"),
        },
        {
            "user_sk": md5("0"),
            "name": "John",
            "age": 23,
            "valid_from": TIME + timedelta(hours=1),
            "valid_to": TIME_INFINITY,
            "_source": "stg__stage",
            "_hash": md5("John-23"),
        },
    ]
