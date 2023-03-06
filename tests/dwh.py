from hnhm import (
    HnHm,
    Layout,
    String,
    FakeSql,
    Integer,
    HnhmLink,
    Timestamp,
    ChangeType,
    HnhmEntity,
    LayoutType,
    HnhmRegistry,
    InMemStorage,
    HnhmLinkElement,
)


class Stage(HnhmEntity):
    """Stage."""

    __layout__ = Layout(name="stage", type=LayoutType.STAGE)

    user_id = String(comment="User ID", change_type=ChangeType.IGNORE)
    review_id = String(comment="Review ID", change_type=ChangeType.IGNORE)
    name = String(comment="User name", change_type=ChangeType.IGNORE)
    age = Integer(comment="User age", change_type=ChangeType.IGNORE)
    time = Timestamp(comment="Time", change_type=ChangeType.IGNORE)


class User(HnhmEntity):
    """User."""

    __layout__ = Layout(name="user", type=LayoutType.HNHM)
    user_id = String(comment="User ID", change_type=ChangeType.IGNORE)
    __keys__ = [user_id]


class Review(HnhmEntity):
    """Review."""

    __layout__ = Layout(name="review", type=LayoutType.HNHM)
    review_id = String(comment="Review ID", change_type=ChangeType.IGNORE)
    __keys__ = [review_id]


class UserReview(HnhmLink):
    """UserReview."""

    __layout__ = Layout(name="user_review")
    user = HnhmLinkElement(entity=User(), comment="User")
    review = HnhmLinkElement(entity=Review(), comment="Review")
    __keys__ = [user, review]


__registry__ = HnhmRegistry(
    entities=[User(), Review()],
    links=[UserReview()],
    hnhm=HnHm(
        sql=FakeSql(),
        storage=InMemStorage(),
    ),
)
