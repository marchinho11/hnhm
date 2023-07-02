import re

import pytest

from hnhm import Flow, HnhmError
from tests.__hnhm__ import (
    UserWith1Key,
    UserWith2Keys,
    ReviewWith1Key,
    StageWith5Columns,
    UserWith1Key1Group,
    LinkUserReviewWith2Keys,
    UserWith1Key1Attribute1Group,
)


def test_no_mapping_for_entity():
    with pytest.raises(
        HnhmError,
        match=(
            "Mapping is required to load data for entity='user'."
            " Please, provide attributes mapping."
        ),
    ):
        Flow(source=StageWith5Columns(), business_time_field=StageWith5Columns.time).load(
            UserWith1Key()
        )


def test_load_is_not_supported_for_non_hnhm():
    with pytest.raises(
        HnhmError,
        match=(
            "Loading is only supported to the entities with the LayoutType='HNHM'."
            " Your target entity='stage' has LayoutType='STAGE'."
        ),
    ):
        Flow(source=StageWith5Columns(), business_time_field=StageWith5Columns.time).load(
            StageWith5Columns(),
            mapping={StageWith5Columns.user_id: StageWith5Columns.user_id},
        )


def test_missing_keys_mappings():
    with pytest.raises(
        HnhmError,
        match=re.escape(
            "Found missing mappings for entity='user' keys."
            " Missing mappings for keys: ['name']."
        ),
    ):
        Flow(source=StageWith5Columns(), business_time_field=StageWith5Columns.time).load(
            UserWith2Keys(),
            mapping={
                UserWith2Keys.user_id: StageWith5Columns.user_id,
            },
        )


def test_missing_group_attributes_mappings():
    with pytest.raises(
        HnhmError,
        match=(
            "Mapping not found for the attribute 'user.name.first_name'."
            " Please, provide all mappings for the group: 'user.name'."
        ),
    ):
        Flow(source=StageWith5Columns(), business_time_field=StageWith5Columns.time).load(
            UserWith1Key1Group(),
            mapping={
                UserWith1Key1Group.user_id: StageWith5Columns.user_id,
                UserWith1Key1Group.last_name: StageWith5Columns.name,
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
            Flow(source=StageWith5Columns(), business_time_field=StageWith5Columns.time)
            .load(
                UserWith1Key(),
                mapping={UserWith1Key.user_id: StageWith5Columns.user_id},
            )
            .load(
                UserWith1Key(),
                mapping={UserWith1Key.user_id: StageWith5Columns.user_id},
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
        Flow(source=UserWith1Key(), business_time_field=StageWith5Columns.time)


def test_no_mapping_required_for_link():
    with pytest.raises(
        HnhmError,
        match=(
            "Keys mapping not found for entity='review'."
            " Please, provide mapping the entity keys."
        ),
    ):
        (
            Flow(source=StageWith5Columns(), business_time_field=StageWith5Columns.time)
            .load(
                UserWith1Key(),
                mapping={UserWith1Key.user_id: StageWith5Columns.user_id},
            )
            .load(LinkUserReviewWith2Keys())
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
            Flow(source=StageWith5Columns(), business_time_field=StageWith5Columns.time)
            .load(
                UserWith1Key(),
                mapping={UserWith1Key.user_id: StageWith5Columns.user_id},
            )
            .load(
                ReviewWith1Key(),
                mapping={ReviewWith1Key.review_id: StageWith5Columns.review_id},
            )
            .load(LinkUserReviewWith2Keys())
            .load(LinkUserReviewWith2Keys())
        )


@pytest.fixture
def flow() -> Flow:
    yield (
        Flow(source=StageWith5Columns(), business_time_field=StageWith5Columns.time)
        .load(
            UserWith1Key1Attribute1Group(),
            mapping={
                UserWith1Key1Attribute1Group.user_id: StageWith5Columns.user_id,
                UserWith1Key1Attribute1Group.first_name: StageWith5Columns.name,
                UserWith1Key1Attribute1Group.last_name: StageWith5Columns.name,
                UserWith1Key1Attribute1Group.age: StageWith5Columns.age,
            },
        )
        .load(
            ReviewWith1Key(),
            mapping={ReviewWith1Key.review_id: StageWith5Columns.review_id},
        )
        .load(LinkUserReviewWith2Keys())
    )


def test_tasks(flow):
    assert [str(t) for t in flow.tasks] == [
        "<LoadHub source='stage' target='user'>",
        "<LoadHub source='stage' target='review'>",
        "<LoadAttribute source='stage' target='user' source_attribute='age' target_attribute='age'>",
        "<LoadGroup 'name' source='stage' target='user'>",
        "<LoadLink 'user_review' source='stage'>",
    ]


def test_ids(flow):
    assert [t.id for t in flow.tasks] == [
        "load_hub__stage__user",
        "load_hub__stage__review",
        "load_attribute__stage_age__user_age",
        "load_group__stage__user_name",
        "load_link__stage__user_review",
    ]


def test_depends_on(flow):
    assert [t.depends_on for t in flow.tasks] == [
        [],
        [],
        ["load_hub__stage__user"],
        ["load_hub__stage__user"],
        ["load_hub__stage__review", "load_hub__stage__user"],
    ]
