import pytest

from hnhm import Layout, HnhmError
from hnhm.hnhm_link import HnhmLink, HnhmLinkElement
from tests.dwh import User, Stage, Review, UserReview


class BaseUserReview(HnhmLink):
    __layout__ = Layout(name="user_review")


def test_no_doc(hnhm):
    class LinkNoDoc(BaseUserReview):
        pass

    with pytest.raises(
        HnhmError,
        match=(
            "Doc not found or empty for link: 'user_review'."
            " Please, write a documentation for your link."
        ),
    ), hnhm:
        hnhm.plan(links=[LinkNoDoc()])


def test_no_layout(hnhm):
    class LinkNoLayout(HnhmLink):
        """LinkNoLayout."""

    with pytest.raises(HnhmError, match="Layout not found for link: "), hnhm:
        hnhm.plan(links=[LinkNoLayout()])


def test_no_elements(hnhm):
    class LinkNoElements(BaseUserReview):
        """LinkNoElements."""

    with pytest.raises(
        HnhmError,
        match=(
            "At least one Key is required for link='user_review'."
            " Please, specify link's keys via the '__keys__' attribute."
        ),
    ), hnhm:
        hnhm.plan(links=[LinkNoElements()])


def test_not_enough_elements(hnhm):
    class LinkNotEnoughElements(BaseUserReview):
        """LinkNotEnoughElements."""

        user = HnhmLinkElement(entity=User(), comment="User")

        __keys__ = [user]

    with pytest.raises(
        HnhmError,
        match=(
            "At least two LinkElements are required for link='user_review'."
            " Please, specify more than one elements."
        ),
    ), hnhm:
        hnhm.plan(links=[LinkNotEnoughElements()])


def test_no_element_comment(hnhm):
    class LinkNoElementComment(BaseUserReview):
        """LinkNoElementComment."""

        user = HnhmLinkElement(entity=User(), comment="")
        review = HnhmLinkElement(entity=Review(), comment="Review")
        __keys__ = [user, review]

    with pytest.raises(
        HnhmError,
        match=(
            "Passed empty comment='' entity='user'."
            " Please, provide a comment for each LinkElement."
        ),
    ), hnhm:
        hnhm.plan(links=[LinkNoElementComment()])


def test_element_not_hnhm(hnhm):
    class LinkElementNotHnhm(BaseUserReview):
        """LinkElementNotHnhm."""

        user = HnhmLinkElement(entity=Stage(), comment="User")
        review = HnhmLinkElement(entity=Review(), comment="Review")
        __keys__ = [user, review]

    with pytest.raises(
        HnhmError,
        match=(
            "Link doesn't support entities with LayoutType='STAGE'."
            " Please, use elements with HNHM layout type."
        ),
    ), hnhm:
        hnhm.plan(links=[LinkElementNotHnhm()])


def test_with_elements(hnhm):
    with hnhm:
        plan = hnhm.plan(links=[UserReview()])

    assert len(plan.mutations_all) == 1
