import pydantic

from .group import Group
from .layout import Layout
from .attribute import Attribute


class Entity(pydantic.BaseModel):
    """Entity core representation."""

    fqn: str
    name: str
    layout: Layout
    doc: str
    keys: list[Attribute]
    attributes: dict[str, Attribute]
    groups: dict[str, Group]

    @property
    def sk(self) -> str:
        return f"{self.name}_sk"

    def __str__(self):
        return f"<Entity '{self.fqn}' layout='{self.layout}'>"

    def __hash__(self):
        return hash(self.fqn)

    def __eq__(self, other):
        return hash(self) == hash(other)
