import pytest

from tests.__hnhm__ import UserWith1Key
from hnhm import Layout, String, Integer, HnhmError, ChangeType, HnhmEntity, LayoutType


def test_no_doc(hnhm):
    class UserNoDoc(UserWith1Key):
        pass

    with hnhm, pytest.raises(
        HnhmError,
        match=(
            "Doc not found or empty for entity: 'HNHM.user'."
            " Please, write a documentation for your entity."
        ),
    ):
        hnhm.plan(entities=[UserNoDoc()])


def test_no_layout(hnhm):
    class NoLayout(HnhmEntity):
        """No layout."""

    with pytest.raises(HnhmError, match="Layout not found for entity: "), hnhm:
        hnhm.plan(entities=[NoLayout()])


def test_no_layout_type(hnhm):
    class UserNoLayoutType(HnhmEntity):
        """UserNoLayoutType."""

        __layout__ = Layout(name="user")

    with pytest.raises(
        HnhmError,
        match=(
            "Type for Layout '<Layout 'user' type='None'>' is required for entity."
            " Please, specify LayoutType via 'type' attribute."
        ),
    ), hnhm:
        hnhm.plan(entities=[UserNoLayoutType()])


def test_unknown_layout_type(hnhm):
    class UserUnknownLayoutType(HnhmEntity):
        """UserUnknownLayoutType."""

        __layout__ = Layout(name="user", type=LayoutType.HNHM)

    # Skip pydantic validation
    hnhm_entity = UserUnknownLayoutType()
    hnhm_entity.__layout__.type = "unknown"

    with pytest.raises(HnhmError, match="Unknown LayoutType='unknown'"), hnhm:
        hnhm.plan(entities=[hnhm_entity])


def test_no_keys_with_hnhm_layout(hnhm):
    class UserNoKeys(HnhmEntity):
        """UserNoKeys."""

        __layout__ = Layout(name="user", type=LayoutType.HNHM)
        user_id = String(comment="User ID", change_type=ChangeType.IGNORE)

    with pytest.raises(HnhmError, match="At least one Key is required for entity "), hnhm:
        hnhm.plan(entities=[UserNoKeys()])


def test_wrong_key_change_type(hnhm):
    class UserWrongChangeType(HnhmEntity):
        """UserWrongChangeType."""

        __layout__ = Layout(name="user", type=LayoutType.HNHM)
        user_id = String(comment="User ID", change_type=ChangeType.NEW)
        __keys__ = [user_id]

    with pytest.raises(
        HnhmError, match="Change type='NEW' is not supported for Key attributes."
    ), hnhm:
        hnhm.plan(entities=[UserWrongChangeType()])


def test_different_group_change_types(hnhm):
    class UserDifferentGroupChangeTypes(UserWith1Key):
        """UserDifferentGroupChangeTypes."""

        name = String(
            comment="User name",
            change_type=ChangeType.NEW,
            group="user_data",
        )
        age = Integer(
            comment="User age",
            change_type=ChangeType.IGNORE,
            group="user_data",
        )

    with pytest.raises(
        HnhmError,
        match=(
            "Found conflicting ChangeType for the entity='HNHM.user' group='user_data'."
            " Please, use single ChangeType for all attributes within the same group."
        ),
    ), hnhm:
        hnhm.plan(entities=[UserDifferentGroupChangeTypes()])


def test_key_only(hnhm):
    class UserKeyOnly(UserWith1Key):
        """UserKeyOnly."""

    with hnhm:
        plan = hnhm.plan(entities=[UserKeyOnly()])
        migrations = plan.migrations_all

    assert [str(m) for m in migrations] == [
        "<CreateEntity 'user'>",
        "<RecreateEntityView 'user'>",
    ]


def test_with_attribute(hnhm):
    class UserWithAttribute(UserWith1Key):
        """UserWithName."""

        name = String(comment="Name.", change_type=ChangeType.IGNORE)

    with hnhm:
        plan = hnhm.plan(entities=[UserWithAttribute()])
        migrations = plan.migrations_all

    assert [str(m) for m in migrations] == [
        "<CreateEntity 'user'>",
        "<CreateAttribute 'name' entity='user'>",
        "<RecreateEntityView 'user'>",
    ]


def test_with_group(hnhm):
    class UserWithGroup(UserWith1Key):
        """UserWithGroup."""

        name = String(comment="Name.", change_type=ChangeType.IGNORE, group="name")

    with hnhm:
        plan = hnhm.plan(entities=[UserWithGroup()])
        migrations = plan.migrations_all

    assert [str(m) for m in migrations] == [
        "<CreateEntity 'user'>",
        "<CreateGroup 'name' entity='user'>",
        "<RecreateEntityView 'user'>",
    ]


def test_update_view(hnhm):
    class UserWithGroup(UserWith1Key):
        """UserWithGroup."""

        name = String(comment="Name.", change_type=ChangeType.IGNORE, group="name")

    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWith1Key()]))

    with hnhm:
        plan = hnhm.plan(entities=[UserWithGroup()])
        migrations = plan.migrations_all

    assert [str(m) for m in migrations] == [
        "<RemoveEntityView 'user'>",
        "<CreateGroup 'name' entity='user'>",
        "<RecreateEntityView 'user'>",
    ]


def test_remove(hnhm):
    class UserWithEverything(UserWith1Key):
        """UserWithEverything."""

        age = Integer(comment="Age.", change_type=ChangeType.IGNORE)
        name = String(comment="Name.", change_type=ChangeType.NEW, group="name")

    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWithEverything()]))

    with hnhm:
        plan = hnhm.plan(entities=[])
        migrations = plan.migrations_all

    assert [str(m) for m in migrations] == [
        "<RemoveEntityView 'user'>",
        "<RemoveAttribute 'age' entity='user'>",
        "<RemoveGroup 'name' entity='user'>",
        "<RemoveEntity 'user'>",
    ]
