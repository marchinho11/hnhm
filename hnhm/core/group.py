import pydantic

from .attribute import Attribute, ChangeType


class Group(pydantic.BaseModel):
    """Group core representation."""

    name: str
    entity_name: str
    attributes: dict[str, Attribute]
    change_type: ChangeType

    @property
    def table(self):
        return f"group__{self.entity_name}__{self.name}"

    def __str__(self):
        return f"<Group '{self.name}' change_type='{self.change_type}'>"

    def __hash__(self):
        return hash(self.table)

    def __eq__(self, other):
        return hash(self) == hash(other)
