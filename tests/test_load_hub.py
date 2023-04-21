from tests.dwh import User, Stage
from hnhm import Flow, String, ChangeType
from tests.util import TIME, md5, get_data, init_dwh


def test_single_pk(hnhm, sqlalchemy_engine):
    stage_data = {
        "user_id": ["user-id-0"],
        "time": [TIME],
    }
    expected_hub_data = {
        "user_sk": [md5("user-id-0")],
        "user_id_bk": ["user-id-0"],
        "valid_from": [TIME],
        "_source": ["stg__stage"],
    }
    init_dwh(
        hnhm=hnhm,
        engine=sqlalchemy_engine,
        entities=[Stage(), User()],
        stage_data={"stg__stage": stage_data},
    )

    flow = Flow(source=Stage(), business_time_field=Stage.time).load(
        User(),
        mapping={User.user_id: Stage.user_id},
    )
    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))

    assert len(flow.tasks) == 1
    assert expected_hub_data == get_data("hub__user", sqlalchemy_engine)


def test_composite_pk(hnhm, sqlalchemy_engine):
    class UserCompositePK(User):
        """UserCompositePK."""

        user_id = String(comment="User id", change_type=ChangeType.IGNORE)
        user_name = String(comment="User Name", change_type=ChangeType.IGNORE)

        __keys__ = [user_id, user_name]

    stage_data = {
        "user_id": ["user-id-0"],
        "name": ["Mark Alonso"],
        "time": [TIME],
    }
    expected_hub_data = {
        "user_sk": [md5("user-id-0-Mark Alonso")],
        "user_id_bk": ["user-id-0"],
        "user_name_bk": ["Mark Alonso"],
        "valid_from": [TIME],
        "_source": ["stg__stage"],
    }
    init_dwh(
        hnhm=hnhm,
        engine=sqlalchemy_engine,
        entities=[Stage(), UserCompositePK()],
        stage_data={"stg__stage": stage_data},
    )

    flow = Flow(source=Stage(), business_time_field=Stage.time).load(
        UserCompositePK(),
        mapping={
            UserCompositePK.user_id: Stage.user_id,
            UserCompositePK.user_name: Stage.name,
        },
    )
    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))

    assert len(flow.tasks) == 1
    assert expected_hub_data == get_data("hub__user", sqlalchemy_engine)
