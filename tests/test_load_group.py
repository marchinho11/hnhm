from datetime import timedelta

from tests.dwh import User, Stage
from hnhm import Flow, String, Integer, ChangeType
from tests.util import TIME, TIME_INFINITY, md5, get_data, init_dwh


def test_ignore(hnhm, sqlalchemy_engine):
    class UserWithGroup(User):
        """UserWithGroup."""

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

    stage_data = {
        "user_id": ["user-id-0"],
        "name": ["Mark Alonso"],
        "age": [100],
        "time": [TIME],
    }
    expected_group_data = {
        "user_sk": [md5("user-id-0")],
        "name": ["Mark Alonso"],
        "age": [100],
        "valid_from": [TIME],
        "_source": ["stg__stage"],
    }
    init_dwh(
        hnhm=hnhm,
        engine=sqlalchemy_engine,
        entities=[Stage(), UserWithGroup()],
        stage_data={"stg__stage": stage_data},
    )

    flow = Flow(source=Stage(), business_time_field=Stage.time).load(
        UserWithGroup(),
        mapping={
            UserWithGroup.user_id: Stage.user_id,
            UserWithGroup.name: Stage.name,
            UserWithGroup.age: Stage.age,
        },
    )
    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))

    assert len(flow.tasks) == 2
    assert expected_group_data == get_data("group__user__user_data", sqlalchemy_engine)

    # Add new data
    stage_data = {
        "user_id": ["user-id-0"],
        "name": ["John Wick"],
        "age": [200],
        "time": [TIME + timedelta(hours=1)],
    }
    init_dwh(hnhm=hnhm, engine=sqlalchemy_engine, stage_data={"stg__stage": stage_data})
    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))

    assert expected_group_data == get_data("group__user__user_data", sqlalchemy_engine)


def test_update(hnhm, sqlalchemy_engine):
    class UserUpdate(User):
        """UserUpdate."""

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

    stage_data = {
        "user_id": ["user-id-0"],
        "name": ["Mark Alonso"],
        "age": [100],
        "time": [TIME],
    }
    expected_group_data = {
        "user_sk": [md5("user-id-0")],
        "name": ["Mark Alonso"],
        "age": [100],
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
            UserUpdate.age: Stage.age,
        },
    )
    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))

    assert len(flow.tasks) == 2
    assert expected_group_data == get_data("group__user__user_data", sqlalchemy_engine)

    # Add new data
    stage_data = {
        "user_id": ["user-id-0"],
        "name": ["John Wick"],
        "age": [200],
        "time": [TIME + timedelta(hours=1)],
    }
    expected_group_data = {
        "user_sk": [md5("user-id-0")],
        "name": ["John Wick"],
        "age": [200],
        "valid_from": [TIME + timedelta(hours=1)],
        "_source": ["stg__stage"],
    }
    init_dwh(hnhm=hnhm, engine=sqlalchemy_engine, stage_data={"stg__stage": stage_data})
    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))

    assert expected_group_data == get_data("group__user__user_data", sqlalchemy_engine)


def test_new(hnhm, sqlalchemy_engine):
    class UserNew(User):
        """UserNew."""

        name = String(comment="User name", change_type=ChangeType.NEW, group="user_data")
        age = Integer(comment="User age", change_type=ChangeType.NEW, group="user_data")

    stage_data = {
        "user_id": ["user-id-0", "user-id-0"],
        "name": ["Mark Alonso", "John Wick"],
        "age": [100, 200],
        "time": [TIME, TIME + timedelta(hours=10)],
    }
    expected_group_data = {
        "user_sk": [md5("user-id-0"), md5("user-id-0")],
        "name": ["Mark Alonso", "John Wick"],
        "age": [100, 200],
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
            UserNew.age: Stage.age,
        },
    )
    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))

    assert len(flow.tasks) == 2
    assert expected_group_data == get_data(
        "group__user__user_data",
        sqlalchemy_engine,
        sort_by=["valid_from"],
    )

    # Add data in the middle
    stage_data = {
        "user_id": ["user-id-0"],
        "name": ["Late Name"],
        "age": [150],
        "time": [TIME + timedelta(hours=5)],
    }
    expected_group_data = {
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
        "age": [
            100,
            150,
            200,
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

    assert expected_group_data == get_data(
        "group__user__user_data",
        engine=sqlalchemy_engine,
        sort_by=["valid_from"],
    )
