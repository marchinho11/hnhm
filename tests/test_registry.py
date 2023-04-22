import pytest

from tests.dwh import User, Review, UserReview
from hnhm import (
    Layout,
    String,
    HnhmLink,
    HnhmError,
    ChangeType,
    HnhmEntity,
    LayoutType,
    HnhmRegistry,
    HnhmLinkElement,
)


def test_duplicated_entity(hnhm):
    class DuplicatedUser(HnhmEntity):
        """DuplicatedUser."""

        __layout__ = Layout(name="user", type=LayoutType.HNHM)
        user_id = String(comment="User ID", change_type=ChangeType.IGNORE)
        __keys__ = [user_id]

    with pytest.raises(
        HnhmError,
        match=(
            "Found duplicated entity: 'HNHM.user'."
            " Please, use unique name for each entity and LayoutType."
        ),
    ):
        HnhmRegistry(entities=[User(), DuplicatedUser()], links=[], hnhm=hnhm)


def test_duplicated_link(hnhm):
    class DuplicatedLink(HnhmLink):
        """DuplicatedLink"""

        __layout__ = Layout(name="user_review")
        user = HnhmLinkElement(entity=User(), comment="User")
        review = HnhmLinkElement(entity=Review(), comment="Review")
        __keys__ = [user, review]

    with pytest.raises(
        HnhmError,
        match=(
            "Found duplicated link: 'user_review'."
            " Please, use unique name for each link."
        ),
    ):
        HnhmRegistry(entities=[], links=[UserReview(), DuplicatedLink()], hnhm=hnhm)
