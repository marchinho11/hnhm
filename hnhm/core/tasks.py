import pydantic

from .link import Link
from .group import Group
from .entity import Entity
from .priority import Priority
from .attribute import Attribute


class Task(pydantic.BaseModel):
    """Flow task."""

    priority: Priority
    source: Entity
    business_time_field: Attribute
    keys_mapping: dict[Attribute, Attribute]


class LoadHub(Task):
    priority = Priority.FIRST
    target: Entity

    def __str__(self):
        return f"<LoadHub source='{self.source.name}' target='{self.target.name}'>"


class LoadAttribute(Task):
    priority = Priority.SECOND
    target: Entity
    source_attribute: Attribute
    target_attribute: Attribute

    def __str__(self):
        return (
            "<LoadAttribute"
            f" source='{self.source.name}'"
            f" target='{self.target.name}'"
            f" source_attribute='{self.source_attribute.name}'"
            f" target_attribute='{self.target_attribute.name}'>"
        )


class LoadGroup(Task):
    priority = Priority.SECOND
    target: Entity
    group: Group
    attributes_mapping: dict[Attribute, Attribute]

    def __str__(self):
        return (
            "<LoadGroup"
            f" source='{self.source.name}'"
            f" target='{self.target.name}'"
            f" group_name='{self.group.name}'>"
        )


class LoadLink(Task):
    priority = Priority.SECOND
    link: Link
    keys_mapping: dict[str, dict[Attribute, Attribute]]

    def __str__(self):
        return f"<LoadLink source='{self.source.name}' link_name='{self.link.name}'>"
