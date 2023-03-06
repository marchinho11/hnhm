from hnhm import Layout, String, Integer, ChangeType, HnhmEntity, LayoutType


class Review(HnhmEntity):
    """Review."""

    __layout__ = Layout(name="review", type=LayoutType.HNHM)

    review_id = String(
        comment="Review ID.",
        change_type=ChangeType.IGNORE,
    )
    user_id = String(
        comment="User ID.",
        change_type=ChangeType.IGNORE,
    )
    text = String(
        comment="Text.",
        change_type=ChangeType.NEW,
        group="review",
    )
    rating = Integer(
        comment="Rating.",
        change_type=ChangeType.NEW,
        group="review",
    )

    __keys__ = [review_id, user_id]
