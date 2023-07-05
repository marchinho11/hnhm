from datetime import timedelta

from hnhm import Flow
from tests.util import TIME, TIME_INFINITY, md5, get_rows, init_dwh, insert_row
from tests.__hnhm__ import (
    UserWith1Key,
    ReviewWith1Key,
    StageWith5Columns,
    LinkUserReviewWith1Key,
    LinkUserReviewWith2Keys,
)


def test_load__single_key(hnhm, cursor):
    init_dwh(
        hnhm=hnhm,
        entities=[UserWith1Key(), ReviewWith1Key(), StageWith5Columns()],
        links=[LinkUserReviewWith1Key()],
        stage_data={"stg__stage": [{"user_id": "0", "review_id": "0", "time": TIME}]},
        cursor=cursor,
    )

    flow = (
        Flow(source=StageWith5Columns(), business_time_field=StageWith5Columns.time)
        .load(
            UserWith1Key(),
            mapping={UserWith1Key.user_id: StageWith5Columns.user_id},
        )
        .load(
            ReviewWith1Key(),
            mapping={ReviewWith1Key.review_id: StageWith5Columns.review_id},
        )
        .load(LinkUserReviewWith1Key())
    )
    flow.execute(hnhm.sql)

    assert len(flow.tasks) == 3
    assert get_rows("link__user_review", cursor) == [
        {
            "user_sk": md5("0"),
            "review_sk": md5("0"),
            "valid_from": TIME,
            "valid_to": TIME_INFINITY,
            "_source": "stg__stage",
        }
    ]

    insert_row(
        "stg__stage",
        {
            "user_id": "0",
            "review_id": "100",
            "time": TIME + timedelta(hours=100),
        },
        cursor,
    )
    flow.execute(hnhm.sql)

    assert get_rows("link__user_review", cursor, order_by="valid_from") == [
        {
            "user_sk": md5("0"),
            "review_sk": md5("0"),
            "valid_from": TIME,
            "valid_to": TIME + timedelta(hours=100),
            "_source": "stg__stage",
        },
        {
            "user_sk": md5("0"),
            "review_sk": md5("100"),
            "valid_from": TIME + timedelta(hours=100),
            "valid_to": TIME_INFINITY,
            "_source": "stg__stage",
        },
    ]


def test_load__multiple_keys(hnhm, cursor):
    init_dwh(
        hnhm=hnhm,
        entities=[UserWith1Key(), ReviewWith1Key(), StageWith5Columns()],
        links=[LinkUserReviewWith2Keys()],
        stage_data={"stg__stage": [{"user_id": "0", "review_id": "0", "time": TIME}]},
        cursor=cursor,
    )

    flow = (
        Flow(source=StageWith5Columns(), business_time_field=StageWith5Columns.time)
        .load(
            UserWith1Key(),
            mapping={UserWith1Key.user_id: StageWith5Columns.user_id},
        )
        .load(
            ReviewWith1Key(),
            mapping={ReviewWith1Key.review_id: StageWith5Columns.review_id},
        )
        .load(LinkUserReviewWith2Keys())
    )
    flow.execute(hnhm.sql)

    assert len(flow.tasks) == 3
    assert get_rows("link__user_review", cursor) == [
        {
            "user_sk": md5("0"),
            "review_sk": md5("0"),
            "valid_from": TIME,
            "valid_to": TIME_INFINITY,
            "_source": "stg__stage",
        }
    ]

    insert_row(
        "stg__stage",
        {
            "user_id": "0",
            "review_id": "100",
            "time": TIME + timedelta(hours=100),
        },
        cursor,
    )
    flow.execute(hnhm.sql)

    assert get_rows("link__user_review", cursor, order_by="valid_from") == [
        {
            "user_sk": md5("0"),
            "review_sk": md5("0"),
            "valid_from": TIME,
            "valid_to": TIME_INFINITY,
            "_source": "stg__stage",
        },
        {
            "user_sk": md5("0"),
            "review_sk": md5("100"),
            "valid_from": TIME + timedelta(hours=100),
            "valid_to": TIME_INFINITY,
            "_source": "stg__stage",
        },
    ]
