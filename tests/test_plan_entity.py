import pytest

from tests.dwh import User
from hnhm.core import CreateGroup, CreateEntity, CreateAttribute
from hnhm import Layout, String, Integer, HnhmError, ChangeType, HnhmEntity, LayoutType


def test_no_doc(hnhm):
    class UserNoDoc(User):
        pass

    with hnhm, pytest.raises(
        HnhmError,
        match=(
            "Doc not found or empty for entity: 'user'."
            " Please, write a documentation for your entity."
        ),
    ):
        hnhm.plan(entities=[UserNoDoc()])


def test_no_layout(hnhm):
    class UserNoLayout(HnhmEntity):
        """UserNoLayout."""

    with pytest.raises(HnhmError, match="Layout not found for entity: "), hnhm:
        hnhm.plan(entities=[UserNoLayout()])


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
    class UserDifferentGroupChangeTypes(User):
        """UserDifferentGroupChangeTypes."""

        name = String(comment="User name", change_type=ChangeType.NEW, group="user_data")
        age = Integer(
            comment="User age", change_type=ChangeType.IGNORE, group="user_data"
        )

    with pytest.raises(
        HnhmError,
        match=(
            "Found conflicting ChangeType for the entity='user' group ='user_data'."
            " Please, use single ChangeType for all attributes within the same group."
        ),
    ), hnhm:
        hnhm.plan(entities=[UserDifferentGroupChangeTypes()])


def test_key_only(hnhm):
    class UserKeyOnly(User):
        """UserKeyOnly."""

    with hnhm:
        plan = hnhm.plan(entities=[UserKeyOnly()])
        mutations = plan.mutations_all

    assert len(mutations) == 1
    mutation = mutations[0]
    assert isinstance(mutation, CreateEntity)
    assert mutation.entity.name == "user"


def test_with_attribute(hnhm):
    class UserWithAttribute(User):
        """UserWithName."""

        name = String(comment="Name.", change_type=ChangeType.IGNORE)

    with hnhm:
        plan = hnhm.plan(entities=[UserWithAttribute()])
        mutations = plan.mutations_all

    assert len(mutations) == 2
    assert isinstance(mutations[0], CreateEntity)
    assert isinstance(mutations[1], CreateAttribute)


def test_with_group(hnhm):
    class UserWithGroup(User):
        """UserWithGroup."""

        name = String(comment="Name.", change_type=ChangeType.IGNORE, group="name")

    with hnhm:
        plan = hnhm.plan(entities=[UserWithGroup()])
        mutations = plan.mutations_all

    assert len(mutations) == 2
    assert isinstance(mutations[0], CreateEntity)
    assert isinstance(mutations[1], CreateGroup)
