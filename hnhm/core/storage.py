import abc

import pydantic

from .link import Link
from .entity import Entity


class HnhmStorageData(pydantic.BaseModel):
    """State data for hnhm."""

    entities: dict[str, Entity]
    links: dict[str, Link]


class Storage(abc.ABC):
    @abc.abstractmethod
    def load(self) -> HnhmStorageData:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, data: HnhmStorageData):
        raise NotImplementedError


class InMemStorage(Storage):
    def load(self) -> HnhmStorageData:
        return HnhmStorageData(entities={}, links={})

    def save(self, data: HnhmStorageData):
        pass
