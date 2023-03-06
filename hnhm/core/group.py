import pydantic

from .attribute import Attribute, ChangeType


class Group(pydantic.BaseModel):
    """Group core representation."""

    name: str
    attributes: dict[str, Attribute]
    change_type: ChangeType

    def __str__(self):
        return f"<Group '{self.name}' change_type='{self.change_type}'>"
