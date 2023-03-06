import abc

from hnhm.core import Type, Attribute, ChangeType


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

        self.owner = None
        self.name = None

    def to_core(self) -> Attribute:
        return Attribute(
            name=self.name,
            comment=self.comment,
            type=self.type,
            change_type=self.change_type,
            group=self.group,
        )

    def __set_name__(self, owner, name):
        self.owner = str(owner)
        self.name = name


class String(HnhmAttribute):
    type = Type.STRING


class Integer(HnhmAttribute):
    type = Type.INTEGER


class Timestamp(HnhmAttribute):
    type = Type.TIMESTAMP
