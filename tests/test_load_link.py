from datetime import timedelta

import pytest

from tests.dwh import User, Stage, Review
from hnhm import Flow, Layout, HnhmLink, HnhmLinkElement
from tests.util import TIME, TIME_INFINITY, md5, get_data, init_dwh


class LinkBase(HnhmLink):
    __layout__ = Layout(name="user_review")


class LinkSinglePK(LinkBase):
    """LinkSinglePK."""

    user = HnhmLinkElement(entity=User(), comment="User")
    review = HnhmLinkElement(entity=Review(), comment="Review")
    __keys__ = [user]


class LinkCompositePK(LinkBase):
    """LinkCompositePK."""

    user = HnhmLinkElement(entity=User(), comment="User")
    review = HnhmLinkElement(entity=Review(), comment="Review")
    __keys__ = [user, review]


@pytest.mark.parametrize("Link", [LinkSinglePK, LinkCompositePK])
def test_load(hnhm, sqlalchemy_engine, Link):
    stage_data = {
        "review_id": ["review-id-0"],
        "user_id": ["user-id-0"],
        "time": [TIME],
    }
    expected_link_data = {
        "review_sk": [md5("review-id-0")],
        "user_sk": [md5("user-id-0")],
        "valid_from": [TIME],
        "valid_to": [TIME_INFINITY],
    }
    init_dwh(
        hnhm=hnhm,
        engine=sqlalchemy_engine,
        entities=[Stage(), User(), Review()],
        links=[Link()],
        stage_data={"stg__stage": stage_data},
    )

    flow = (
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
    )
    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))

    assert len(flow.tasks) == 3
    assert expected_link_data == get_data("link__user_review", sqlalchemy_engine)

    # Add new link ts
    stage_data = {
        "review_id": ["review-id-0"],
        "user_id": ["user-id-0"],
        "time": [TIME + timedelta(hours=100)],
    }
    expected_link_data = {
        "review_sk": [md5("review-id-0"), md5("review-id-0")],
        "user_sk": [md5("user-id-0"), md5("user-id-0")],
        "valid_from": [TIME, TIME + timedelta(hours=100)],
        "valid_to": [TIME + timedelta(hours=100), TIME_INFINITY],
    }
    init_dwh(
        hnhm=hnhm,
        engine=sqlalchemy_engine,
        stage_data={"stg__stage": stage_data},
    )
    for task in flow.tasks:
        hnhm.sql.execute(hnhm.sql.generate_sql(task))

    assert expected_link_data == get_data(
        "link__user_review",
        sqlalchemy_engine,
        sort_by=["valid_from"],
    )
