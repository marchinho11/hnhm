import itertools
from datetime import timedelta

from hnhm import Flow, Integer, ChangeType
from tests.util import TIME, TIME_INFINITY, md5, get_rows, init_dwh, insert_row
from tests.__hnhm__ import UserWith2Keys, StageWith5Columns, UserWith1Key1Attribute


def test_ignore(hnhm, cursor):
    init_dwh(
        hnhm=hnhm,
        entities=[StageWith5Columns(), UserWith1Key1Attribute()],
        stage_data={"stg__stage": [{"user_id": "0", "age": 15, "time": TIME}]},
        cursor=cursor,
    )

    flow = Flow(
        source=StageWith5Columns(), business_time_field=StageWith5Columns.time
    ).load(
        UserWith1Key1Attribute(),
        mapping={
            UserWith1Key1Attribute.user_id: StageWith5Columns.user_id,
            UserWith1Key1Attribute.age: StageWith5Columns.age,
        },
    )

    expected = [
        {
            "user_sk": md5("0"),
            "age": 15,
            "valid_from": TIME,
            "_source": "stg__stage",
            "_hash": md5("15"),
        }
    ]

    flow.execute(hnhm.sql)
    assert len(flow.tasks) == 2
    assert get_rows("attr__user__age", cursor) == expected

    insert_row(
        "stg__stage",
        {"user_id": "0", "age": 100, "time": TIME},
        cursor,
    )
    flow.execute(hnhm.sql)
    assert get_rows("attr__user__age", cursor) == expected


def test_update(hnhm, cursor):
    class UserUpdate(UserWith1Key1Attribute):
        """UserUpdate."""

        age = Integer("User age", change_type=ChangeType.UPDATE)

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
    flow.execute(hnhm.sql)

    assert len(flow.tasks) == 2
    assert get_rows("attr__user__age", cursor) == [
        {
            "user_sk": md5("0"),
            "age": 15,
            "valid_from": TIME,
            "_source": "stg__stage",
            "_hash": md5("15"),
        }
    ]

    insert_row(
        "stg__stage",
        {"user_id": "0", "age": 100, "time": TIME + timedelta(hours=1)},
        cursor,
    )
    flow.execute(hnhm.sql)
    assert get_rows("attr__user__age", cursor) == [
        {
            "user_sk": md5("0"),
            "age": 100,
            "valid_from": TIME + timedelta(hours=1),
            "_source": "stg__stage",
            "_hash": md5("100"),
        }
    ]


def test_new__1key(hnhm, cursor):
    class UserNew(UserWith1Key1Attribute):
        """UserNew."""

        age = Integer("User age", change_type=ChangeType.NEW)

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
    flow.execute(hnhm.sql)

    assert len(flow.tasks) == 2
    assert get_rows("attr__user__age", cursor, order_by="valid_from") == [
        {
            "user_sk": md5("0"),
            "age": 15,
            "valid_from": TIME,
            "valid_to": TIME_INFINITY,
            "_source": "stg__stage",
            "_hash": md5("15"),
        }
    ]

    insert_row(
        "stg__stage",
        {"user_id": "0", "age": 100, "time": TIME + timedelta(hours=24)},
        cursor,
    )
    flow.execute(hnhm.sql)

    assert get_rows("attr__user__age", cursor, order_by="valid_from") == [
        {
            "user_sk": md5("0"),
            "age": 15,
            "valid_from": TIME,
            "valid_to": TIME + timedelta(hours=24),
            "_source": "stg__stage",
            "_hash": md5("15"),
        },
        {
            "user_sk": md5("0"),
            "age": 100,
            "valid_from": TIME + timedelta(hours=24),
            "valid_to": TIME_INFINITY,
            "_source": "stg__stage",
            "_hash": md5("100"),
        },
    ]

    # Insert in the "middle"
    insert_row(
        "stg__stage",
        {"user_id": "0", "age": 500, "time": TIME + timedelta(hours=10)},
        cursor,
    )
    flow.execute(hnhm.sql)
    assert get_rows("attr__user__age", cursor, order_by="valid_from") == [
        {
            "user_sk": md5("0"),
            "age": 15,
            "valid_from": TIME,
            "valid_to": TIME + timedelta(hours=10),
            "_source": "stg__stage",
            "_hash": md5("15"),
        },
        {
            "user_sk": md5("0"),
            "age": 500,
            "valid_from": TIME + timedelta(hours=10),
            "valid_to": TIME + timedelta(hours=24),
            "_source": "stg__stage",
            "_hash": md5("500"),
        },
        {
            "user_sk": md5("0"),
            "age": 100,
            "valid_from": TIME + timedelta(hours=24),
            "valid_to": TIME_INFINITY,
            "_source": "stg__stage",
            "_hash": md5("100"),
        },
    ]


def test_new__2keys(hnhm, cursor):
    class UserNew(UserWith2Keys):
        """UserNew."""

        age = Integer("User age", change_type=ChangeType.NEW)

    init_dwh(
        hnhm=hnhm,
        entities=[StageWith5Columns(), UserNew()],
        stage_data={
            "stg__stage": [{"user_id": "0", "name": "mark", "age": 15, "time": TIME}]
        },
        cursor=cursor,
    )

    flow = Flow(
        source=StageWith5Columns(), business_time_field=StageWith5Columns.time
    ).load(
        UserNew(),
        mapping={
            UserNew.user_id: StageWith5Columns.user_id,
            UserNew.name: StageWith5Columns.name,
            UserNew.age: StageWith5Columns.age,
        },
    )
    flow.execute(hnhm.sql)

    assert len(flow.tasks) == 2
    assert get_rows("attr__user__age", cursor, order_by="valid_from") == [
        {
            "user_sk": md5("0-mark"),
            "age": 15,
            "valid_from": TIME,
            "valid_to": TIME_INFINITY,
            "_source": "stg__stage",
            "_hash": md5("15"),
        }
    ]

    insert_row(
        "stg__stage",
        {"user_id": "0", "name": "mark", "age": 100, "time": TIME + timedelta(hours=24)},
        cursor,
    )
    insert_row(
        "stg__stage",
        {"user_id": "100", "name": "mad", "age": 500, "time": TIME},
        cursor,
    )
    insert_row(
        "stg__stage",
        {"user_id": "0", "name": "mark", "age": 1000, "time": TIME + timedelta(hours=12)},
        cursor,
    )
    flow.execute(hnhm.sql)

    rows = get_rows("attr__user__age", cursor)

    by_user_sk = {}
    for user_sk, rows_by_user in itertools.groupby(rows, lambda u: u["user_sk"]):
        by_user_sk[user_sk] = sorted(rows_by_user, key=lambda x: x["valid_from"])

    assert by_user_sk == {
        md5("0-mark"): [
            {
                "user_sk": md5("0-mark"),
                "age": 15,
                "valid_from": TIME,
                "valid_to": TIME + timedelta(hours=12),
                "_source": "stg__stage",
                "_hash": md5("15"),
            },
            {
                "user_sk": md5("0-mark"),
                "age": 1000,
                "valid_from": TIME + timedelta(hours=12),
                "valid_to": TIME + timedelta(hours=24),
                "_source": "stg__stage",
                "_hash": md5("1000"),
            },
            {
                "user_sk": md5("0-mark"),
                "age": 100,
                "valid_from": TIME + timedelta(hours=24),
                "valid_to": TIME_INFINITY,
                "_source": "stg__stage",
                "_hash": md5("100"),
            },
        ],
        md5("100-mad"): [
            {
                "user_sk": md5("100-mad"),
                "age": 500,
                "valid_from": TIME,
                "valid_to": TIME_INFINITY,
                "_source": "stg__stage",
                "_hash": md5("500"),
            }
        ],
    }


def test_new__2keys__duplicates(hnhm, cursor):
    class UserNew(UserWith2Keys):
        """UserNew."""

        age = Integer("User age", change_type=ChangeType.NEW)

    row = {"user_id": "0", "name": "mark", "age": 15, "time": TIME}
    expected = [
        {
            "user_sk": md5("0-mark"),
            "age": 15,
            "valid_from": TIME,
            "valid_to": TIME_INFINITY,
            "_source": "stg__stage",
            "_hash": md5("15"),
        }
    ]

    init_dwh(
        hnhm=hnhm,
        entities=[StageWith5Columns(), UserNew()],
        stage_data={"stg__stage": [row]},
        cursor=cursor,
    )

    flow = Flow(
        source=StageWith5Columns(), business_time_field=StageWith5Columns.time
    ).load(
        UserNew(),
        mapping={
            UserNew.user_id: StageWith5Columns.user_id,
            UserNew.name: StageWith5Columns.name,
            UserNew.age: StageWith5Columns.age,
        },
    )
    flow.execute(hnhm.sql)

    assert len(flow.tasks) == 2
    assert get_rows("attr__user__age", cursor, order_by="valid_from") == expected

    insert_row("stg__stage", row, cursor)
    insert_row("stg__stage", row, cursor)
    insert_row("stg__stage", row, cursor)
    flow.execute(hnhm.sql)

    assert get_rows("attr__user__age", cursor, order_by="valid_from") == expected
