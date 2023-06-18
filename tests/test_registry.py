import pytest

from hnhm import HnhmError, HnhmRegistry
from tests.__hnhm__ import UserWith1Key, LinkUserReviewWith2Keys


def test_duplicated_entity(hnhm):
    class DuplicatedUser(UserWith1Key):
        """DuplicatedUser."""

    with pytest.raises(
        HnhmError,
        match=(
            "Found duplicated entity: 'HNHM.user'."
            " Please, use unique name for each entity."
        ),
    ):
        HnhmRegistry(entities=[UserWith1Key(), DuplicatedUser()], links=[], hnhm=hnhm)


def test_duplicated_link(hnhm):
    class DuplicatedLink(LinkUserReviewWith2Keys):
        """DuplicatedLink"""

    with pytest.raises(
        HnhmError,
        match=(
            "Found duplicated link: 'user_review'."
            " Please, use unique name for each link."
        ),
    ):
        HnhmRegistry(
            entities=[], links=[LinkUserReviewWith2Keys(), DuplicatedLink()], hnhm=hnhm
        )
