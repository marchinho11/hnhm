import pytest

from tests.dwh import User
from hnhm import Layout, String, HnhmError, ChangeType, LayoutType
from tests.util import get_views_in_database, get_column_names_for_table


def test_only_sk(hnhm, sqlalchemy_engine):
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[User()]))
    assert get_views_in_database(sqlalchemy_engine) == {"entity__user"}
    assert get_column_names_for_table(sqlalchemy_engine, "entity__user") == {"user_sk"}


def test_fail_on_second_delete(hnhm, sqlalchemy_engine):
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[User()]))

    with hnhm:
        plan = hnhm.plan(entities=[])
        hnhm.apply(plan)

    with pytest.raises(HnhmError, match="Entity's View 'user' doesn't exist."), hnhm:
        with hnhm:
            hnhm.apply(plan)


class UserWithAttributeAndGroup(User):
    """UserWithAttributeAndGroup."""

    __layout__ = Layout(name="user", type=LayoutType.HNHM)
    user_id = String(comment="User ID", change_type=ChangeType.IGNORE)
    name = String(comment="Name.", change_type=ChangeType.IGNORE)
    last_name = String(comment="Last name.", change_type=ChangeType.UPDATE)
    age = String(comment="Age.", change_type=ChangeType.NEW)
    gender = String(
        comment="Gender.", change_type=ChangeType.IGNORE, group="identification"
    )
    religion = String(
        comment="Religion.", change_type=ChangeType.UPDATE, group="religiosity"
    )
    phone = String(comment="Phone.", change_type=ChangeType.NEW, group="contacts")
    mail = String(comment="Mail.", change_type=ChangeType.NEW, group="contacts")
    __keys__ = [user_id]


def test_with_attributes_and_groups(hnhm, sqlalchemy_engine):
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWithAttributeAndGroup()]))
    assert get_views_in_database(sqlalchemy_engine) == {"entity__user"}
    assert get_column_names_for_table(sqlalchemy_engine, "entity__user") == {
        "user_sk",
        "name",
        "last_name",
        "age",
        "identification__gender",
        "religiosity__religion",
        "contacts__phone",
        "contacts__mail",
    }
