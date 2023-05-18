import abc

import pydantic

from .link import Link
from .entity import Entity
from .error import HnhmError


class HnhmStorageData(pydantic.BaseModel):
    """State data for hnhm."""

    entities: dict[str, Entity]
    entities_views: set[str]
    links: dict[str, Link]

    def check_entity_exists(self, entity: str):
        if entity not in self.entities:
            raise HnhmError(f"Entity '{entity}' doesn't exist.")

    def check_entity_not_exists(self, entity: str):
        if entity in self.entities:
            raise HnhmError(f"Entity '{entity}' already exists.")

    def check_link_exists(self, link: str):
        if link not in self.links:
            raise HnhmError(f"Link '{link}' doesn't exist.")

    def check_link_not_exists(self, link: str):
        if link in self.links:
            raise HnhmError(f"Link '{link}' already exists.")

    def check_attribute_exists(self, entity: str, attribute: str):
        self.check_entity_exists(entity)
        if attribute not in self.entities[entity].attributes:
            raise HnhmError(f"Attribute '{attribute}' doesn't exist.")

    def check_attribute_not_exists(self, entity: str, attribute: str):
        self.check_entity_exists(entity)
        if attribute in self.entities[entity].attributes:
            raise HnhmError(f"Attribute '{attribute}' already exists.")

    def check_group_exists(self, entity: str, group: str):
        self.check_entity_exists(entity)
        if group not in self.entities[entity].groups:
            raise HnhmError(f"Group '{group}' doesn't exist.")

    def check_group_not_exists(self, entity: str, group: str):
        self.check_entity_exists(entity)
        if group in self.entities[entity].groups:
            raise HnhmError(f"Group '{group}' already exists.")

    def check_group_attribute_exists(self, entity: str, group: str, attribute: str):
        self.check_group_exists(entity, group)
        if attribute not in self.entities[entity].groups[group].attributes:
            raise HnhmError(f"Attribute '{attribute}' doesn't exist.")

    def check_group_attribute_not_exists(self, entity: str, group: str, attribute: str):
        self.check_group_exists(entity, group)
        if attribute in self.entities[entity].groups[group].attributes:
            raise HnhmError(f"Attribute '{attribute}' already exists.")


class Storage(abc.ABC):
    @abc.abstractmethod
    def load(self) -> HnhmStorageData:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, data: HnhmStorageData):
        raise NotImplementedError


class InMemStorage(Storage):
    def load(self) -> HnhmStorageData:
        return HnhmStorageData(entities={}, entities_views=set(), links={})

    def save(self, data: HnhmStorageData):
        pass
