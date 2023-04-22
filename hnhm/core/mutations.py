import pydantic

from .link import Link
from .group import Group
from .entity import Entity
from .priority import Priority
from .attribute import Attribute


class Mutation(pydantic.BaseModel):
    """Mutation represents DWH change."""

    priority: Priority


class CreateEntity(Mutation):
    priority = Priority.FIRST
    entity: Entity

    def __str__(self):
        return f"<CreateEntity '{self.entity.name}'>"


class RemoveEntity(Mutation):
    priority = Priority.SECOND
    entity: Entity

    def __str__(self):
        return f"<RemoveEntity '{self.entity.name}'>"


class CreateAttribute(Mutation):
    priority = Priority.SECOND
    entity: Entity
    attribute: Attribute

    def __str__(self):
        return f"<CreateAttribute '{self.attribute.name}' entity='{self.entity.name}'>"


class RemoveAttribute(Mutation):
    priority = Priority.FIRST
    entity: Entity
    attribute: Attribute

    def __str__(self):
        return f"<RemoveAttribute '{self.attribute.name}' entity='{self.entity.name}'>"


class CreateGroup(Mutation):
    priority = Priority.SECOND
    entity: Entity
    group: Group

    def __str__(self):
        return f"<CreateGroup '{self.group.name}' entity='{self.entity.name}'>"


class RemoveGroup(Mutation):
    priority = Priority.FIRST
    entity: Entity
    group: Group

    def __str__(self):
        return f"<RemoveGroup '{self.group.name}' entity='{self.entity.name}'>"


class AddGroupAttribute(Mutation):
    """Add an Attribute to an existing Group."""

    priority = Priority.SECOND
    entity: Entity
    group: Group
    attribute: Attribute

    def __str__(self):
        return (
            f"<AddGroupAttribute '{self.group.name}'"
            f" entity='{self.entity.name}'"
            f" attribute='{self.attribute.name}'>"
        )


class RemoveGroupAttribute(Mutation):
    """Remove an Attribute from an existing Group."""

    priority = Priority.SECOND
    entity: Entity
    group: Group
    attribute: Attribute

    def __str__(self):
        return (
            f"<RemoveGroupAttribute '{self.group.name}'"
            f" entity='{self.entity.name}'"
            f" attribute='{self.attribute.name}'>"
        )


class CreateLink(Mutation):
    priority = Priority.SECOND
    link: Link

    def __str__(self):
        return f"<CreateLink '{self.link.name}'>"


class RemoveLink(Mutation):
    priority = Priority.FIRST
    link: Link

    def __str__(self):
        return f"<RemoveLink '{self.link.name}'>"
