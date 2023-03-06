import re

import pytest

from tests.dwh import User, Stage, Review
from hnhm import Flow, Layout, String, HnhmLink, HnhmError, ChangeType, HnhmLinkElement


def test_no_mapping_for_entity():
    with pytest.raises(
        HnhmError,
        match=(
            "Mapping is required to load data for entity='user'."
            " Please, provide attributes mapping."
        ),
    ):
        Flow(source=Stage(), business_time_field=Stage.time).load(User())


def test_load_is_not_supported_for_non_hnhm():
    with pytest.raises(
        HnhmError,
        match=(
            "Loading is only supported to the entities with the LayoutType='HNHM'."
            " Your target entity='stage' has LayoutType='STAGE'."
        ),
    ):
        Flow(source=Stage(), business_time_field=Stage.time).load(
            Stage(), mapping={Stage.user_id: Stage.user_id}
        )


class UserCompositePK(User):
    """UserCompositePK."""

    user_id = String(comment="User id", change_type=ChangeType.IGNORE)
    name = String(comment="User name", change_type=ChangeType.IGNORE)
    __keys__ = [user_id, name]


def test_missing_keys_mappings():
    with pytest.raises(
        HnhmError,
        match=re.escape(
            "Found missing mappings for entity='user' keys."
            " Missing mappings for keys: ['name']."
        ),
    ):
        Flow(source=Stage(), business_time_field=Stage.time).load(
            UserCompositePK(),
            mapping={
                UserCompositePK.user_id: Stage.user_id,
            },
        )


def test_not_single_load_for_entity():
    with pytest.raises(
        HnhmError,
        match=re.escape(
            "Found duplicated load for entity='user'."
            " Please, use single load() block for single entity."
        ),
    ):
        (
            Flow(source=Stage(), business_time_field=Stage.time)
            .load(
                User(),
                mapping={User.user_id: Stage.user_id},
            )
            .load(
                User(),
                mapping={User.user_id: Stage.user_id},
            )
        )


def test_load_only_from_stage():
    with pytest.raises(
        HnhmError,
        match=re.escape(
            "Flow doesn't support loading from entities with layout type 'HNHM'."
            " Please, use Flow to load data only from STAGE entities."
        ),
    ):
        Flow(source=User(), business_time_field=Stage.time)


class Link(HnhmLink):
    """Link."""

    __layout__ = Layout(name="user_review")
    user = HnhmLinkElement(entity=User(), comment="User")
    review = HnhmLinkElement(entity=Review(), comment="Review")
    __keys__ = [user, review]


def test_no_mapping_required_for_link():
    with pytest.raises(
        HnhmError,
        match=(
            "Keys mapping not found for entity='review'."
            " Please, provide mapping the entity keys."
        ),
    ):
        (
            Flow(source=Stage(), business_time_field=Stage.time)
            .load(
                User(),
                mapping={User.user_id: Stage.user_id},
            )
            .load(Link())
        )


def test_not_single_load_for_link():
    with pytest.raises(
        HnhmError,
        match=re.escape(
            "Found duplicated load for link='user_review'."
            " Please, use single load() block for single link."
        ),
    ):
        (
            Flow(source=Stage(), business_time_field=Stage.time)
            .load(
                User(),
                mapping={User.user_id: Stage.user_id},
            )
            .load(
                Review(),
                mapping={Review.review_id: Stage.review_id},
            )
            .load(Link())
            .load(Link())
        )
