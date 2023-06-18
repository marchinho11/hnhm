"""TODO: Fix and test the case when we have a link with 1 Key"""
from datetime import timedelta

from hnhm import Flow
from tests.util import TIME, TIME_INFINITY, md5, get_rows, init_dwh, insert_row
from tests.__hnhm__ import (
    UserWith1Key,
    ReviewWith1Key,
    StageWith5Columns,
    LinkUserReviewWith2Keys,
)


def test_load__multiple_keys(hnhm, cursor):
    init_dwh(
        hnhm=hnhm,
        entities=[UserWith1Key(), ReviewWith1Key(), StageWith5Columns()],
        links=[LinkUserReviewWith2Keys()],
        stage_data={
            "stg__stage": [
                {
                    "review_id": "0",
                    "user_id": "0",
                    "time": TIME,
                }
            ]
        },
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
    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))

    assert len(flow.tasks) == 3
    assert get_rows("link__user_review", cursor) == [
        {
            "review_sk": md5("0"),
            "user_sk": md5("0"),
            "valid_from": TIME,
            "valid_to": TIME_INFINITY,
            "_source": "stg__stage",
        }
    ]

    # Add new link ts
    insert_row(
        "stg__stage",
        {
            "review_id": "0",
            "user_id": "0",
            "time": TIME + timedelta(hours=100),
        },
        cursor,
    )

    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))

    assert get_rows("link__user_review", cursor, order_by="valid_from") == [
        {
            "review_sk": md5("0"),
            "user_sk": md5("0"),
            "valid_from": TIME,
            "valid_to": TIME + timedelta(hours=100),
            "_source": "stg__stage",
        },
        {
            "review_sk": md5("0"),
            "user_sk": md5("0"),
            "valid_from": TIME + timedelta(hours=100),
            "valid_to": TIME_INFINITY,
            "_source": "stg__stage",
        },
    ]
