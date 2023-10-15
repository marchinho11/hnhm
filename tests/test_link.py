import pytest

from hnhm import Layout, HnhmError
from hnhm.hnhm_link import HnhmLink, HnhmLinkElement
from tests.util import get_views, get_tables, get_columns
from tests.__hnhm__ import (
    UserWith1Key,
    ReviewWith1Key,
    StageWith5Columns,
    LinkUserReviewWith2Keys,
)


def test_works(hnhm, cursor):
    with hnhm:
        hnhm.apply(
            hnhm.plan(
                entities=[UserWith1Key(), ReviewWith1Key()],
                links=[LinkUserReviewWith2Keys()],
            )
        )
    assert get_tables(cursor) == {"hub__user", "hub__review", "link__user_review"}
    assert get_views(cursor) == {"entity__user", "entity__review"}
    assert get_columns("link__user_review", cursor) == {
        "user_sk",
        "review_sk",
        "valid_from",
        "valid_to",
        "_source",
        "_loaded_at",
    }

    with hnhm:
        hnhm.apply(hnhm.plan(entities=[], links=[]))
    assert not get_tables(cursor)
    assert not get_views(cursor)


def test_no_doc(hnhm):
    class NoDoc(HnhmLink):
        __layout__ = Layout(name="no_doc")

    with pytest.raises(
        HnhmError,
        match=(
            "Doc not found or empty for link: 'no_doc'."
            " Please, write a documentation for your link."
        ),
    ), hnhm:
        hnhm.plan(links=[NoDoc()])


def test_no_layout(hnhm):
    class NoLayout(HnhmLink):
        """NoLayout."""

    with pytest.raises(HnhmError, match="Layout not found for link: "), hnhm:
        hnhm.plan(links=[NoLayout()])


def test_no_elements(hnhm):
    class NoElements(HnhmLink):
        """NoElements."""

        __layout__ = Layout(name="no_elements")

    with pytest.raises(
        HnhmError,
        match=(
            "At least one Key is required for 'no_elements'."
            " Please, specify link's keys via the '__keys__' attribute."
        ),
    ), hnhm:
        hnhm.plan(links=[NoElements()])


def test_not_enough_elements(hnhm):
    class NotEnoughElements(HnhmLink):
        """NotEnoughElements."""

        __layout__ = Layout(name="not_enough_elements")
        user = HnhmLinkElement("User", entity=UserWith1Key())
        __keys__ = [user]

    with pytest.raises(
        HnhmError,
        match=(
            "At least two LinkElements are required for 'not_enough_elements'."
            " Please, specify more than one elements."
        ),
    ), hnhm:
        hnhm.plan(links=[NotEnoughElements()])


def test_no_element_comment(hnhm):
    class NoElementComment(HnhmLink):
        """NoElementComment."""

        __layout__ = Layout(name="no_element_comment")
        user = HnhmLinkElement("", entity=UserWith1Key())
        review = HnhmLinkElement("Review", entity=ReviewWith1Key())
        __keys__ = [user, review]

    with pytest.raises(
        HnhmError,
        match=(
            "Passed empty comment='' entity='user'."
            " Please, provide a comment for each LinkElement."
        ),
    ), hnhm:
        hnhm.plan(links=[NoElementComment()])


def test_element_not_hnhm(hnhm):
    class ElementNotHnhm(HnhmLink):
        """ElementNotHnhm."""

        __layout__ = Layout(name="element_not_hnhm")
        user = HnhmLinkElement("User", entity=StageWith5Columns())
        review = HnhmLinkElement("Review", entity=ReviewWith1Key())
        __keys__ = [user, review]

    with pytest.raises(
        HnhmError,
        match=(
            "Link doesn't support entities with LayoutType='STAGE'."
            " Please, use elements with HNHM layout type."
        ),
    ), hnhm:
        hnhm.plan(links=[ElementNotHnhm()])


def test_with_elements(hnhm):
    with hnhm:
        plan = hnhm.plan(links=[LinkUserReviewWith2Keys()])

    assert len(plan.migrations_all) == 1
