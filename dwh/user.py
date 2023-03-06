from hnhm import Layout, String, ChangeType, HnhmEntity, LayoutType


class User(HnhmEntity):
    """User."""

    __layout__ = Layout(name="user", type=LayoutType.HNHM)

    user_id = String(
        comment="User ID.",
        change_type=ChangeType.IGNORE,
    )
    name = String(
        comment="Name.",
        change_type=ChangeType.NEW,
    )

    __keys__ = [user_id]
