from hnhm.core.sql import FakeSql
from hnhm.core.state import InMemState
from hnhm import (
    HnHm,
    Layout,
    String,
    Integer,
    HnhmLink,
    Timestamp,
    ChangeType,
    HnhmEntity,
    LayoutType,
    HnhmRegistry,
    HnhmLinkElement,
)


class StageNoColumns(HnhmEntity):
    """Stage without columns."""

    __layout__ = Layout(name="stage", type=LayoutType.STAGE)


class StageWith1Column(StageNoColumns):
    """Stage with 1 column."""

    user_id = String("User ID", change_type=ChangeType.IGNORE)


class StageWith5Columns(StageWith1Column):
    """Stage with 5 columns."""

    review_id = String("Review ID", change_type=ChangeType.IGNORE)
    name = String("User name", change_type=ChangeType.IGNORE)
    age = Integer("User age", change_type=ChangeType.IGNORE)
    time = Timestamp("Time", change_type=ChangeType.IGNORE)


class StageWith6Columns(StageWith5Columns):
    """Stage with 6 columns."""

    new_id = String("New ID", change_type=ChangeType.IGNORE)


class UserWith1Key(HnhmEntity):
    """User with 1 key."""

    __layout__ = Layout(name="user", type=LayoutType.HNHM)
    user_id = String("User ID", change_type=ChangeType.IGNORE)
    __keys__ = [user_id]


class UserWith2Keys(UserWith1Key):
    """User with 2 keys."""

    user_id = String("User ID", change_type=ChangeType.IGNORE)
    name = String("User name", change_type=ChangeType.IGNORE)
    __keys__ = [user_id, name]


class UserWith1Key1Attribute(UserWith1Key):
    """User with 1 key and 1 attribute."""

    age = Integer("User age", change_type=ChangeType.IGNORE)


class UserWith1Key1Group(UserWith1Key):
    """User with 1 key and 1 group."""

    first_name = String(
        "First name.",
        change_type=ChangeType.IGNORE,
        group="name",
    )
    last_name = String(
        "Last name.",
        change_type=ChangeType.IGNORE,
        group="name",
    )


class UserWith1Key1GroupExtraAttribute(UserWith1Key1Group):
    """User with 1 key and 1 group. Group have an extra attribute."""

    third_name = String(
        "Third name.",
        change_type=ChangeType.IGNORE,
        group="name",
    )


class UserWith1Key1Attribute1Group(UserWith1Key1Attribute, UserWith1Key1Group):
    """User with 1 key, 1 attribute, and 1 group."""


class ReviewWith1Key(HnhmEntity):
    """Review with 1 key."""

    __layout__ = Layout(name="review", type=LayoutType.HNHM)
    review_id = String("Review ID", change_type=ChangeType.IGNORE)
    __keys__ = [review_id]


class LinkUserReviewWith1Key(HnhmLink):
    """Link UserReview with 1 key."""

    __layout__ = Layout(name="user_review")
    user = HnhmLinkElement("User", entity=UserWith1Key())
    review = HnhmLinkElement("Review", entity=ReviewWith1Key())
    __keys__ = [user]


class LinkUserReviewWith2Keys(HnhmLink):
    """Link UserReview with 2 keys."""

    __layout__ = Layout(name="user_review")
    user = HnhmLinkElement("User", entity=UserWith1Key())
    review = HnhmLinkElement("Review", entity=ReviewWith1Key())
    __keys__ = [user, review]


registry = HnhmRegistry(
    entities=[UserWith1Key(), ReviewWith1Key()],
    links=[LinkUserReviewWith2Keys()],
    hnhm=HnHm(
        sql=FakeSql(),
        state=InMemState(),
    ),
)
