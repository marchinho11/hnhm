from hnhm import Layout, String, Integer, ChangeType, HnhmEntity, LayoutType


class User(HnhmEntity):
    """User data."""

    __layout__ = Layout(name="user", type=LayoutType.HNHM)

    user_id = String(comment="User ID.", change_type=ChangeType.IGNORE)
    age = Integer(comment="Age.", change_type=ChangeType.UPDATE)
    first_name = String(comment="First name.", change_type=ChangeType.NEW, group="name")
    last_name = String(comment="Last name.", change_type=ChangeType.NEW, group="name")

    __keys__ = [user_id]
