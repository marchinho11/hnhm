import abc

import pydantic

from .link import Link
from .entity import Entity
from .error import HnhmError


class HnhmStateData(pydantic.BaseModel):
    """State data for hnhm."""

    entities: dict[str, Entity]
    entities_views: set[str]
    links: dict[str, Link]

    def check_entity_exists(self, entity_fqn: str):
        if entity_fqn not in self.entities:
            raise HnhmError(f"Entity '{entity_fqn}' doesn't exist.")

    def check_entity_not_exists(self, entity_fqn: str):
        if entity_fqn in self.entities:
            raise HnhmError(f"Entity '{entity_fqn}' already exists.")

    def check_link_exists(self, link_fqn: str):
        if link_fqn not in self.links:
            raise HnhmError(f"Link '{link_fqn}' doesn't exist.")

    def check_link_not_exists(self, link: str):
        if link in self.links:
            raise HnhmError(f"Link '{link}' already exists.")

    def check_attribute_exists(self, entity_fqn: str, attribute: str):
        self.check_entity_exists(entity_fqn)
        if attribute not in self.entities[entity_fqn].attributes:
            raise HnhmError(f"Attribute '{attribute}' doesn't exist.")

    def check_attribute_not_exists(self, entity_fqn: str, attribute: str):
        self.check_entity_exists(entity_fqn)
        if attribute in self.entities[entity_fqn].attributes:
            raise HnhmError(f"Attribute '{attribute}' already exists.")

    def check_group_exists(self, entity_fqn: str, group: str):
        self.check_entity_exists(entity_fqn)
        if group not in self.entities[entity_fqn].groups:
            raise HnhmError(f"Group '{group}' doesn't exist.")

    def check_group_not_exists(self, entity_fqn: str, group: str):
        self.check_entity_exists(entity_fqn)
        if group in self.entities[entity_fqn].groups:
            raise HnhmError(f"Group '{group}' already exists.")

    def check_group_attribute_exists(self, entity_fqn: str, group: str, attribute: str):
        self.check_group_exists(entity_fqn, group)
        if attribute not in self.entities[entity_fqn].groups[group].attributes:
            raise HnhmError(f"Attribute '{attribute}' doesn't exist.")

    def check_group_attribute_not_exists(
        self, entity_fqn: str, group: str, attribute: str
    ):
        self.check_group_exists(entity_fqn, group)
        if attribute in self.entities[entity_fqn].groups[group].attributes:
            raise HnhmError(f"Attribute '{attribute}' already exists.")


class State(abc.ABC):
    @abc.abstractmethod
    def load(self) -> HnhmStateData:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, data: HnhmStateData):
        raise NotImplementedError


class InMemState(State):
    def load(self) -> HnhmStateData:
        return HnhmStateData(entities={}, entities_views=set(), links={})

    def save(self, data: HnhmStateData):
        pass
