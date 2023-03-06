import pydantic

from .entity import Entity
from .layout import Layout


class LinkElement(pydantic.BaseModel):
    """Link element."""

    entity: Entity
    comment: str

    def __str__(self):
        return f"<LinkElement entity='{self.entity.name}'>"

    def __hash__(self):
        return hash(self.entity.name)

    def __eq__(self, other):
        return hash(self) == hash(other)


class Link(pydantic.BaseModel):
    """Link core representation."""

    name: str
    doc: str
    layout: Layout
    elements: list[LinkElement]
    keys: list[LinkElement]

    def __str__(self):
        return f"<Link '{self.name}' layout='{self.layout}'>"
