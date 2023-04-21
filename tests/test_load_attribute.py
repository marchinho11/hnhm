from datetime import timedelta

from tests.dwh import User, Stage
from hnhm import Flow, String, ChangeType
from tests.util import TIME, TIME_INFINITY, md5, get_data, init_dwh


def test_ignore(hnhm, sqlalchemy_engine):
    class UserIgnore(User):
        """UserIgnore."""

        name = String(comment="User name", change_type=ChangeType.IGNORE)

    stage_data = {
        "user_id": ["user-id-0"],
        "name": ["Mark Alonso"],
        "time": [TIME],
    }
    expected_attribute_data = {
        "user_sk": [md5("user-id-0")],
        "name": ["Mark Alonso"],
        "valid_from": [TIME],
        "_source": ["stg__stage"],
    }
    init_dwh(
        hnhm=hnhm,
        engine=sqlalchemy_engine,
        entities=[Stage(), UserIgnore()],
        stage_data={"stg__stage": stage_data},
    )

    flow = Flow(source=Stage(), business_time_field=Stage.time).load(
        UserIgnore(),
        mapping={
            UserIgnore.user_id: Stage.user_id,
            UserIgnore.name: Stage.name,
        },
    )
    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))

    assert len(flow.tasks) == 2
    assert expected_attribute_data == get_data("attr__user__name", sqlalchemy_engine)

    # Add new data
    stage_data = {
        "user_id": ["user-id-0"],
        "name": ["John Wick"],
        "time": [TIME + timedelta(hours=1)],
    }
    init_dwh(hnhm=hnhm, engine=sqlalchemy_engine, stage_data={"stg__stage": stage_data})
    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))

    assert expected_attribute_data == get_data("attr__user__name", sqlalchemy_engine)


def test_update(hnhm, sqlalchemy_engine):
    class UserUpdate(User):
        """UserUpdate."""

        name = String(comment="User name", change_type=ChangeType.UPDATE)

    stage_data = {
        "user_id": ["user-id-0"],
        "name": ["Mark Alonso"],
        "time": [TIME],
    }
    expected_attribute_data = {
        "user_sk": [md5("user-id-0")],
        "name": ["Mark Alonso"],
        "valid_from": [TIME],
        "_source": ["stg__stage"],
    }
    init_dwh(
        hnhm=hnhm,
        engine=sqlalchemy_engine,
        entities=[Stage(), UserUpdate()],
        stage_data={"stg__stage": stage_data},
    )

    flow = Flow(source=Stage(), business_time_field=Stage.time).load(
        UserUpdate(),
        mapping={
            UserUpdate.user_id: Stage.user_id,
            UserUpdate.name: Stage.name,
        },
    )
    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))

    assert len(flow.tasks) == 2
    assert expected_attribute_data == get_data("attr__user__name", sqlalchemy_engine)

    # Add new data
    stage_data = {
        "user_id": ["user-id-0"],
        "name": ["John Wick"],
        "time": [TIME + timedelta(hours=1)],
    }
    expected_attribute_data = {
        "user_sk": [md5("user-id-0")],
        "name": ["John Wick"],
        "valid_from": [TIME + timedelta(hours=1)],
        "_source": ["stg__stage"],
    }
    init_dwh(hnhm=hnhm, engine=sqlalchemy_engine, stage_data={"stg__stage": stage_data})
    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))

    assert expected_attribute_data == get_data("attr__user__name", sqlalchemy_engine)


def test_new(hnhm, sqlalchemy_engine):
    class UserNew(User):
        """UserNew."""

        user_id = String(comment="User id", change_type=ChangeType.IGNORE)
        name = String(comment="User name", change_type=ChangeType.NEW)

    stage_data = {
        "user_id": ["user-id-0", "user-id-0"],
        "name": ["Mark Alonso", "John Wick"],
        "time": [TIME, TIME + timedelta(hours=10)],
    }
    expected_attribute_data = {
        "user_sk": [md5("user-id-0"), md5("user-id-0")],
        "name": ["Mark Alonso", "John Wick"],
        "valid_from": [TIME, TIME + timedelta(hours=10)],
        "valid_to": [TIME + timedelta(hours=10), TIME_INFINITY],
        "_source": ["stg__stage", "stg__stage"],
    }
    init_dwh(
        hnhm=hnhm,
        engine=sqlalchemy_engine,
        entities=[Stage(), UserNew()],
        stage_data={"stg__stage": stage_data},
    )

    flow = Flow(source=Stage(), business_time_field=Stage.time).load(
        UserNew(),
        mapping={
            UserNew.user_id: Stage.user_id,
            UserNew.name: Stage.name,
        },
    )
    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))

    assert len(flow.tasks) == 2
    assert expected_attribute_data == get_data(
        "attr__user__name",
        sqlalchemy_engine,
        sort_by=["valid_from"],
    )

    # Add data in the middle
    stage_data = {
        "user_id": ["user-id-0"],
        "name": ["Late Name"],
        "time": [TIME + timedelta(hours=5)],
    }
    expected_attribute_data = {
        "user_sk": [
            md5("user-id-0"),
            md5("user-id-0"),
            md5("user-id-0"),
        ],
        "name": [
            "Mark Alonso",
            "Late Name",
            "John Wick",
        ],
        "valid_from": [
            TIME,
            TIME + timedelta(hours=5),
            TIME + timedelta(hours=10),
        ],
        "valid_to": [
            TIME + timedelta(hours=5),
            TIME + timedelta(hours=10),
            TIME_INFINITY,
        ],
        "_source": [
            "stg__stage",
            "stg__stage",
            "stg__stage",
        ],
    }
    init_dwh(hnhm=hnhm, engine=sqlalchemy_engine, stage_data={"stg__stage": stage_data})
    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))

    assert expected_attribute_data == get_data(
        "attr__user__name",
        sqlalchemy_engine,
        sort_by=["valid_from"],
    )
