from hnhm import Flow
from tests.util import TIME, md5, get_rows, init_dwh
from tests.__hnhm__ import UserWith2Keys, StageWith5Columns, UserWith1Key1Attribute


def test_single_pk(hnhm, cursor):
    init_dwh(
        hnhm=hnhm,
        entities=[StageWith5Columns(), UserWith1Key1Attribute()],
        stage_data={"stg__stage": [{"user_id": "0", "time": TIME}]},
        cursor=cursor,
    )

    flow = Flow(
        source=StageWith5Columns(), business_time_field=StageWith5Columns.time
    ).load(
        UserWith1Key1Attribute(),
        mapping={UserWith1Key1Attribute.user_id: StageWith5Columns.user_id},
    )
    flow.execute(hnhm.sql)

    assert len(flow.tasks) == 1
    assert get_rows("hub__user", cursor) == [
        {
            "user_sk": md5("0"),
            "user_id_bk": "0",
            "valid_from": TIME,
            "_source": "stg__stage",
        }
    ]


def test_composite_pk(hnhm, cursor):
    init_dwh(
        hnhm=hnhm,
        entities=[StageWith5Columns(), UserWith2Keys()],
        stage_data={"stg__stage": [{"user_id": "0", "name": "Name", "time": TIME}]},
        cursor=cursor,
    )

    flow = Flow(
        source=StageWith5Columns(), business_time_field=StageWith5Columns.time
    ).load(
        UserWith2Keys(),
        mapping={
            UserWith2Keys.user_id: StageWith5Columns.user_id,
            UserWith2Keys.name: StageWith5Columns.name,
        },
    )
    flow.execute(hnhm.sql)

    assert len(flow.tasks) == 1
    assert get_rows("hub__user", cursor) == [
        {
            "user_sk": md5("0-Name"),
            "user_id_bk": "0",
            "name_bk": "Name",
            "valid_from": TIME,
            "_source": "stg__stage",
        }
    ]
