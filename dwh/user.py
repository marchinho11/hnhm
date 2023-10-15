from hnhm import Layout, String, Integer, ChangeType, HnhmEntity, LayoutType


class User(HnhmEntity):
    """User data."""

    __layout__ = Layout(name="user", type=LayoutType.HNHM)

    user_id = String("User ID.", change_type=ChangeType.IGNORE)
    age = Integer("Age.", change_type=ChangeType.UPDATE)
    first_name = String("First name.", change_type=ChangeType.NEW, group="name")
    last_name = String("Last name.", change_type=ChangeType.NEW, group="name")

    __keys__ = [user_id]
