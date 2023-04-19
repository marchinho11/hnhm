from tests.dwh import User, Stage
from hnhm import String, Integer, ChangeType
from tests.util import get_tables_in_database, get_column_names_for_table


def test_stage(hnhm, sqlalchemy_engine):
    # Create
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[Stage()]))
    assert get_tables_in_database(sqlalchemy_engine) == {"stg__stage"}

    # Cleanup
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[]))
    assert not get_tables_in_database(sqlalchemy_engine)


def test_ignore_add_attribute_to_stage(hnhm, sqlalchemy_engine):
    """This is in backlog: add/remove a column from a stage table."""

    # Create
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[Stage()]))
    assert get_tables_in_database(sqlalchemy_engine) == {"stg__stage"}
    assert get_column_names_for_table(sqlalchemy_engine, "stg__stage") == {
        "user_id",
        "review_id",
        "name",
        "age",
        "time",
    }

    class StageNewAttribute(Stage):
        """StageNewAttribute."""

        new_id = String(comment="New ID", change_type=ChangeType.IGNORE)

    # Add new Attribute
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[StageNewAttribute()]))
    assert get_column_names_for_table(sqlalchemy_engine, "stg__stage") == {
        "user_id",
        "review_id",
        "name",
        "age",
        "time",
    }


def test_hub_only(hnhm, sqlalchemy_engine):
    class UserHubOnly(User):
        """UserHubOnly"""

    # Create
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserHubOnly()]))
    assert get_tables_in_database(sqlalchemy_engine) == {"hub__user"}

    # Cleanup
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[]))
    assert not get_tables_in_database(sqlalchemy_engine)


def test_with_attribute(hnhm, sqlalchemy_engine):
    class UserWithAttr(User):
        """UserWithAttr"""

        name = String(comment="Name.", change_type=ChangeType.IGNORE)

    # Create
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWithAttr()]))
    assert get_tables_in_database(sqlalchemy_engine) == {"hub__user", "attr__user__name"}

    # Cleanup
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[]))
    assert not get_tables_in_database(sqlalchemy_engine)


def test_attribute_operations(hnhm, sqlalchemy_engine):
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[User()]))
    assert get_tables_in_database(sqlalchemy_engine) == {"hub__user"}

    # Add attribute
    class UserWithAttr(User):
        """UserWithNewAttr"""

        age = Integer(comment="Age.", change_type=ChangeType.IGNORE)

    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWithAttr()]))
    assert get_tables_in_database(sqlalchemy_engine) == {"hub__user", "attr__user__age"}

    # Remove attribute
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[User()]))
    assert get_tables_in_database(sqlalchemy_engine) == {"hub__user"}


def test_with_group(hnhm, sqlalchemy_engine):
    class UserWithGroup(User):
        """UserWithGroup"""

        first_name = String(
            comment="First name.", change_type=ChangeType.IGNORE, group="name"
        )
        last_name = String(
            comment="Last name.", change_type=ChangeType.IGNORE, group="name"
        )

    # Create
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWithGroup()]))
    assert get_tables_in_database(sqlalchemy_engine) == {"hub__user", "group__user__name"}

    # Cleanup
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[]))
    assert not get_tables_in_database(sqlalchemy_engine)


def test_group__create_remove(hnhm, sqlalchemy_engine):
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[User()]))
    assert get_tables_in_database(sqlalchemy_engine) == {"hub__user"}

    # Add group
    class UserWithGroup(User):
        """UserWithGroup"""

        first_name = String(
            comment="First name.", change_type=ChangeType.IGNORE, group="name"
        )
        last_name = String(
            comment="Last name.", change_type=ChangeType.IGNORE, group="name"
        )

    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWithGroup()]))
    assert get_tables_in_database(sqlalchemy_engine) == {"hub__user", "group__user__name"}

    # Remove group
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[User()]))
    assert get_tables_in_database(sqlalchemy_engine) == {"hub__user"}


def test_with_attribute_and_group(hnhm, sqlalchemy_engine):
    class UserWithAttrAndGroup(User):
        """User"""

        age = Integer(
            comment="Age.",
            change_type=ChangeType.IGNORE,
        )
        first_name = String(
            comment="First name.",
            change_type=ChangeType.IGNORE,
            group="name",
        )
        last_name = String(
            comment="Last name.",
            change_type=ChangeType.IGNORE,
            group="name",
        )

    # Create
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWithAttrAndGroup()]))
    assert get_tables_in_database(sqlalchemy_engine) == {
        "hub__user",
        "attr__user__age",
        "group__user__name",
    }

    # Cleanup
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[]))
    assert not get_tables_in_database(sqlalchemy_engine)


def test_group_add_remove_attribute(hnhm, sqlalchemy_engine):
    class UserWithGroup(User):
        """UserWithGroup"""

        first_name = String(
            comment="First name.", change_type=ChangeType.IGNORE, group="name"
        )

    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWithGroup()]))
    assert get_tables_in_database(sqlalchemy_engine) == {"hub__user", "group__user__name"}
    assert get_column_names_for_table(sqlalchemy_engine, "group__user__name") == {
        "user_sk",
        "first_name",
        "valid_from",
    }

    # Add an Attribute to a Group
    class UserAddAttributeToGroup(User):
        """UserAddAttributeToGroup"""

        first_name = String(
            comment="First name.", change_type=ChangeType.IGNORE, group="name"
        )
        last_name = String(
            comment="Last name.", change_type=ChangeType.IGNORE, group="name"
        )

    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserAddAttributeToGroup()]))
    assert get_column_names_for_table(sqlalchemy_engine, "group__user__name") == {
        "user_sk",
        "first_name",
        "last_name",
        "valid_from",
    }

    # Remove an Attribute from a Group
    class UserRemoveAttributeFromAGroup(User):
        """UserRemoveAttributeFromAGroup"""

        last_name = String(
            comment="Last name.", change_type=ChangeType.IGNORE, group="name"
        )

    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserRemoveAttributeFromAGroup()]))
    assert get_column_names_for_table(sqlalchemy_engine, "group__user__name") == {
        "user_sk",
        "last_name",
        "valid_from",
    }

    # Remove Group
    class UserRemoveGroup(User):
        """UserRemoveGroup"""

    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserRemoveGroup()]))
    assert get_tables_in_database(sqlalchemy_engine) == {"hub__user"}
