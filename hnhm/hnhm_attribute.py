import abc

from .core.attribute import Type
from .core import Attribute, ChangeType


class HnhmAttribute(abc.ABC):
    type: Type

    def __init__(
        self,
        *,
        comment: str,
        change_type: ChangeType,
        group: str | None = None,
    ):
        self.comment = comment
        self.change_type = change_type
        self.group = group
        self.name = None

    def to_core(self, entity_name: str) -> Attribute:
        return Attribute(
            name=self.name,
            entity_name=entity_name,
            comment=self.comment,
            type=self.type,
            change_type=self.change_type,
            group=self.group,
        )

    def __set_name__(self, _, name):
        self.name = name


class String(HnhmAttribute):
    type = Type.STRING


class Integer(HnhmAttribute):
    type = Type.INTEGER


class Float(HnhmAttribute):
    type = Type.FLOAT


class Timestamp(HnhmAttribute):
    type = Type.TIMESTAMP
