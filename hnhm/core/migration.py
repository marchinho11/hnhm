"""
Create Entity order:
    1. Create Entity
    2. Create Attribute, Group
    3. Recreate Entity's view

Update Entity order:
    1. Remove Entity's view
    2. Create Entity
    3. Create Attribute, Group
    4. Recreate Entity's view

Remove Entity order:
    1. Remove Entity's view
    2. Remove Attribute, Group
    3. Remove Entity
"""
import pydantic

from .link import Link
from .group import Group
from .entity import Entity
from .priority import Priority
from .attribute import Attribute


class Migration(pydantic.BaseModel):
    priority: Priority


class CreateEntity(Migration):
    priority: Priority = Priority.FIRST
    entity: Entity

    def __str__(self):
        return f"<CreateEntity '{self.entity.name}'>"


class RemoveEntity(Migration):
    priority: Priority = Priority.THIRD
    entity: Entity

    def __str__(self):
        return f"<RemoveEntity '{self.entity.name}'>"


class RecreateEntityView(Migration):
    priority: Priority = Priority.THIRD
    entity: Entity

    def __str__(self):
        return f"<RecreateEntityView '{self.entity.name}'>"


class RemoveEntityView(Migration):
    priority: Priority = Priority.FIRST
    entity: Entity

    def __str__(self):
        return f"<RemoveEntityView '{self.entity.name}'>"


class CreateAttribute(Migration):
    priority: Priority = Priority.SECOND
    entity: Entity
    attribute: Attribute

    def __str__(self):
        return f"<CreateAttribute '{self.attribute.name}' entity='{self.entity.name}'>"


class RemoveAttribute(Migration):
    priority: Priority = Priority.SECOND
    entity: Entity
    attribute: Attribute

    def __str__(self):
        return f"<RemoveAttribute '{self.attribute.name}' entity='{self.entity.name}'>"


class CreateGroup(Migration):
    priority: Priority = Priority.SECOND
    entity: Entity
    group: Group

    def __str__(self):
        return f"<CreateGroup '{self.group.name}' entity='{self.entity.name}'>"


class RemoveGroup(Migration):
    priority: Priority = Priority.SECOND
    entity: Entity
    group: Group

    def __str__(self):
        return f"<RemoveGroup '{self.group.name}' entity='{self.entity.name}'>"


class AddGroupAttribute(Migration):
    """Add an Attribute to an existing Group."""

    priority: Priority = Priority.SECOND
    entity: Entity
    group: Group
    attribute: Attribute

    def __str__(self):
        return (
            f"<AddGroupAttribute '{self.group.name}'"
            f" entity='{self.entity.name}'"
            f" attribute='{self.attribute.name}'>"
        )


class RemoveGroupAttribute(Migration):
    """Remove an Attribute from an existing Group."""

    priority: Priority = Priority.SECOND
    entity: Entity
    group: Group
    attribute: Attribute

    def __str__(self):
        return (
            f"<RemoveGroupAttribute '{self.group.name}'"
            f" entity='{self.entity.name}'"
            f" attribute='{self.attribute.name}'>"
        )


class CreateLink(Migration):
    priority: Priority = Priority.SECOND
    link: Link

    def __str__(self):
        return f"<CreateLink '{self.link.name}'>"


class RemoveLink(Migration):
    priority: Priority = Priority.FIRST
    link: Link

    def __str__(self):
        return f"<RemoveLink '{self.link.name}'>"
