from abc import abstractmethod

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
    depends_on: list[str] = []

    @property
    @abstractmethod
    def id(self):
        raise NotImplementedError


class LoadHub(Task):
    priority: Priority = Priority.FIRST
    target: Entity

    @property
    def id(self):
        return f"load_hub__{self.source.name}__{self.target.name}"

    def __str__(self):
        return f"<LoadHub source='{self.source.name}' target='{self.target.name}'>"


class LoadAttribute(Task):
    priority: Priority = Priority.SECOND
    target: Entity
    source_attribute: Attribute
    target_attribute: Attribute

    @property
    def id(self):
        return (
            "load_attribute"
            f"__{self.source.name}_{self.source_attribute.name}"
            f"__{self.target.name}_{self.target_attribute.name}"
        )

    def __str__(self):
        return (
            "<LoadAttribute"
            f" source='{self.source.name}'"
            f" target='{self.target.name}'"
            f" source_attribute='{self.source_attribute.name}'"
            f" target_attribute='{self.target_attribute.name}'>"
        )


class LoadGroup(Task):
    priority: Priority = Priority.SECOND
    target: Entity
    group: Group
    attributes_mapping: dict[Attribute, Attribute]

    @property
    def id(self):
        return (
            f"load_group"
            f"__{self.source.name}"
            f"__{self.target.name}_{self.group.name}"
        )

    def __str__(self):
        return (
            f"<LoadGroup '{self.group.name}'"
            f" source='{self.source.name}'"
            f" target='{self.target.name}'>"
        )


class LoadLink(Task):
    priority: Priority = Priority.SECOND
    link: Link
    key_entities_names: list[str]
    keys_mapping: dict[str, dict[Attribute, Attribute]]

    @property
    def id(self):
        return f"load_link__{self.source.name}__{self.link.name}"

    def __str__(self):
        return f"<LoadLink '{self.link.name}' source='{self.source.name}'>"
