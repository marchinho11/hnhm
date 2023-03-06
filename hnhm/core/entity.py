import pydantic

from .group import Group
from .layout import Layout
from .attribute import Attribute


class Entity(pydantic.BaseModel):
    """Entity core representation."""

    name: str
    layout: Layout
    doc: str
    keys: list[Attribute]
    attributes: dict[str, Attribute]
    groups: dict[str, Group]

    def __str__(self):
        return f"<Entity '{self.name}' layout='{self.layout}'>"

    def __hash__(self):
        return hash(f"{self.name}_{self.layout.type}")

    def __eq__(self, other):
        return hash(self) == hash(other)
