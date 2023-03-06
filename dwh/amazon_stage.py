from hnhm import Layout, String, Integer, Timestamp, ChangeType, HnhmEntity, LayoutType


class AmazonStg(HnhmEntity):
    """Stage Amazon data with user reviews."""

    __layout__ = Layout(name="amazon", type=LayoutType.STAGE)

    user_id = String(
        comment="User ID.",
        change_type=ChangeType.IGNORE,
    )
    review_id = String(
        comment="Review ID.",
        change_type=ChangeType.IGNORE,
    )
    name = String(
        comment="User Name.",
        change_type=ChangeType.IGNORE,
    )
    rating = Integer(
        comment="Rating.",
        change_type=ChangeType.IGNORE,
    )
    text = String(
        comment="Review text.",
        change_type=ChangeType.IGNORE,
    )
    time = Timestamp(
        comment="Time.",
        change_type=ChangeType.IGNORE,
    )
