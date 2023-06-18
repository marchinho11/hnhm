"""TODO: broken test for NEW"""
from datetime import timedelta

from hnhm import Flow, String, Integer, ChangeType
from tests.__hnhm__ import UserWith1Key, StageWith5Columns
from tests.util import TIME, TIME_INFINITY, md5, get_rows, init_dwh, insert_row


class GroupIgnore(UserWith1Key):
    """Group Ignore."""

    name = String(
        comment="User name",
        change_type=ChangeType.IGNORE,
        group="user_data",
    )
    age = Integer(
        comment="User age",
        change_type=ChangeType.IGNORE,
        group="user_data",
    )


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
    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))

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

    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))

    assert len(flow.tasks) == 2
    assert get_rows("group__user__user_data", cursor) == expected


class GroupUpdate(UserWith1Key):
    """Group Update."""

    name = String(
        comment="User name",
        change_type=ChangeType.UPDATE,
        group="user_data",
    )
    age = Integer(
        comment="User age",
        change_type=ChangeType.UPDATE,
        group="user_data",
    )


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
    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))

    assert len(flow.tasks) == 2
    assert get_rows("group__user__user_data", cursor) == [
        {
            "user_sk": md5("0"),
            "name": "Mark",
            "age": 100,
            "valid_from": TIME,
            "_source": "stg__stage",
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

    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))

    assert len(flow.tasks) == 2
    assert get_rows("group__user__user_data", cursor) == [
        {
            "user_sk": md5("0"),
            "name": "John",
            "age": 23,
            "valid_from": TIME + timedelta(hours=1),
            "_source": "stg__stage",
        }
    ]


class GroupNew(UserWith1Key):
    """Group New."""

    name = String(
        comment="User name",
        change_type=ChangeType.NEW,
        group="user_data",
    )
    age = Integer(
        comment="User age",
        change_type=ChangeType.NEW,
        group="user_data",
    )


#
#
# def test_new(hnhm, cursor):
#     init_dwh(
#         hnhm=hnhm,
#         entities=[StageWith5Columns(), GroupNew()],
#         stage_data={
#             "stg__stage": [
#                 {
#                     "user_id": "0",
#                     "name": "Mark",
#                     "age": 100,
#                     "time": TIME,
#                 }
#             ]
#         },
#         cursor=cursor,
#     )
#
#     flow = Flow(
#         source=StageWith5Columns(), business_time_field=StageWith5Columns.time
#     ).load(
#         GroupNew(),
#         mapping={
#             GroupNew.user_id: StageWith5Columns.user_id,
#             GroupNew.name: StageWith5Columns.name,
#             GroupNew.age: StageWith5Columns.age,
#         },
#     )
#     for task in flow.tasks:
#         hnhm.sql.execute(hnhm.sql.generate_sql(task))
#
#     assert len(flow.tasks) == 2
#     assert get_rows("group__user__user_data", cursor) == [
#         {
#             "user_sk": md5("0"),
#             "name": "Mark",
#             "age": 100,
#             "valid_from": TIME,
#             "_source": "stg__stage",
#         }
#     ]
#
#     # Add new data
#     insert_row(
#         "stg__stage",
#         {
#             "user_id": "0",
#             "name": "John",
#             "age": 23,
#             "time": TIME + timedelta(hours=1),
#         },
#         cursor,
#     )
#
#     for task in flow.tasks:
#         hnhm.sql.execute(hnhm.sql.generate_sql(task))
#
#     assert len(flow.tasks) == 2
#     assert get_rows("group__user__user_data", cursor, order_by="valid_from") == [
#         {
#             "user_sk": md5("0"),
#             "name": "Mark",
#             "age": 100,
#             "valid_from": TIME,
#             "valid_to": TIME + timedelta(hours=1),
#             "_source": "stg__stage",
#         },
#         {
#             "user_sk": md5("0"),
#             "name": "John",
#             "age": 23,
#             "valid_from": TIME + timedelta(hours=1),
#             "valid_to": TIME_INFINITY,
#             "_source": "stg__stage",
#         },
#     ]
