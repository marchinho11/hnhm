from datetime import timedelta

from hnhm import Flow, Integer, ChangeType
from tests.__hnhm__ import StageWith5Columns, UserWith1Key1Attribute
from tests.util import TIME, TIME_INFINITY, md5, get_rows, init_dwh, insert_row


def test_ignore(hnhm, cursor):
    init_dwh(
        hnhm=hnhm,
        entities=[StageWith5Columns(), UserWith1Key1Attribute()],
        stage_data={"stg__stage": [{"user_id": "0", "age": 15, "time": TIME}]},
        cursor=cursor,
    )

    expected = [
        {
            "user_sk": md5("0"),
            "age": 15,
            "valid_from": TIME,
            "_source": "stg__stage",
        }
    ]

    flow = Flow(
        source=StageWith5Columns(), business_time_field=StageWith5Columns.time
    ).load(
        UserWith1Key1Attribute(),
        mapping={
            UserWith1Key1Attribute.user_id: StageWith5Columns.user_id,
            UserWith1Key1Attribute.age: StageWith5Columns.age,
        },
    )
    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))
    assert len(flow.tasks) == 2
    assert get_rows("attr__user__age", cursor) == expected

    insert_row(
        "stg__stage",
        {"user_id": "0", "age": 100, "time": TIME},
        cursor,
    )
    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))
    assert get_rows("attr__user__age", cursor) == expected


def test_update(hnhm, cursor):
    class UserUpdate(UserWith1Key1Attribute):
        """UserUpdate."""

        age = Integer(comment="User age", change_type=ChangeType.UPDATE)

    init_dwh(
        hnhm=hnhm,
        entities=[StageWith5Columns(), UserUpdate()],
        stage_data={"stg__stage": [{"user_id": "0", "age": 15, "time": TIME}]},
        cursor=cursor,
    )

    flow = Flow(
        source=StageWith5Columns(), business_time_field=StageWith5Columns.time
    ).load(
        UserUpdate(),
        mapping={
            UserUpdate.user_id: StageWith5Columns.user_id,
            UserUpdate.age: StageWith5Columns.age,
        },
    )
    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))
    assert len(flow.tasks) == 2
    assert get_rows("attr__user__age", cursor) == [
        {
            "user_sk": md5("0"),
            "age": 15,
            "valid_from": TIME,
            "_source": "stg__stage",
        }
    ]

    insert_row(
        "stg__stage",
        {"user_id": "0", "age": 100, "time": TIME + timedelta(hours=1)},
        cursor,
    )
    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))
    assert get_rows("attr__user__age", cursor) == [
        {
            "user_sk": md5("0"),
            "age": 100,
            "valid_from": TIME + timedelta(hours=1),
            "_source": "stg__stage",
        }
    ]


def test_new(hnhm, cursor):
    class UserNew(UserWith1Key1Attribute):
        """UserNew."""

        age = Integer(comment="User age", change_type=ChangeType.NEW)

    init_dwh(
        hnhm=hnhm,
        entities=[StageWith5Columns(), UserNew()],
        stage_data={"stg__stage": [{"user_id": "0", "age": 15, "time": TIME}]},
        cursor=cursor,
    )

    flow = Flow(
        source=StageWith5Columns(), business_time_field=StageWith5Columns.time
    ).load(
        UserNew(),
        mapping={
            UserNew.user_id: StageWith5Columns.user_id,
            UserNew.age: StageWith5Columns.age,
        },
    )
    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))

    assert len(flow.tasks) == 2
    assert get_rows("attr__user__age", cursor, order_by="valid_from") == [
        {
            "user_sk": md5("0"),
            "age": 15,
            "valid_from": TIME,
            "valid_to": TIME_INFINITY,
            "_source": "stg__stage",
        }
    ]

    insert_row(
        "stg__stage",
        {"user_id": "0", "age": 100, "time": TIME + timedelta(hours=24)},
        cursor,
    )
    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))
    assert get_rows("attr__user__age", cursor, order_by="valid_from") == [
        {
            "user_sk": md5("0"),
            "age": 15,
            "valid_from": TIME,
            "valid_to": TIME + timedelta(hours=24),
            "_source": "stg__stage",
        },
        {
            "user_sk": md5("0"),
            "age": 100,
            "valid_from": TIME + timedelta(hours=24),
            "valid_to": TIME_INFINITY,
            "_source": "stg__stage",
        },
    ]

    # Insert in the "middle"
    insert_row(
        "stg__stage",
        {"user_id": "0", "age": 500, "time": TIME + timedelta(hours=10)},
        cursor,
    )
    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))
    assert get_rows("attr__user__age", cursor, order_by="valid_from") == [
        {
            "user_sk": md5("0"),
            "age": 15,
            "valid_from": TIME,
            "valid_to": TIME + timedelta(hours=10),
            "_source": "stg__stage",
        },
        {
            "user_sk": md5("0"),
            "age": 500,
            "valid_from": TIME + timedelta(hours=10),
            "valid_to": TIME + timedelta(hours=24),
            "_source": "stg__stage",
        },
        {
            "user_sk": md5("0"),
            "age": 100,
            "valid_from": TIME + timedelta(hours=24),
            "valid_to": TIME_INFINITY,
            "_source": "stg__stage",
        },
    ]
