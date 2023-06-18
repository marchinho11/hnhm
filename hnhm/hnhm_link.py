import abc
import inspect

from .hnhm_entity import HnhmEntity
from .core import Link, Layout, HnhmError, LayoutType, LinkElement


class HnhmLinkElement:
    def __init__(self, *, entity: HnhmEntity, comment: str):
        self.entity = entity
        self.comment = comment

    def to_core(self) -> LinkElement:
        entity = self.entity.to_core()
        if entity.layout.type != LayoutType.HNHM:
            raise HnhmError(
                f"Link doesn't support entities with LayoutType='{entity.layout.type}'."
                " Please, use elements with HNHM layout type."
            )

        if not self.comment:
            raise HnhmError(
                f"Passed empty comment='{self.comment}' entity='{entity.name}'."
                " Please, provide a comment for each LinkElement."
            )

        return LinkElement(entity=entity, comment=self.comment)


class HnhmLink(abc.ABC):
    __layout__: Layout
    __keys__: list[HnhmEntity]

    def to_core(self) -> Link:
        inspected = dict(inspect.getmembers(self))

        if not inspected.get("__layout__"):
            raise HnhmError(
                f"Layout not found for link: '{self}'."
                " Please, specify Layout via '__layout__' attribute."
            )
        layout: Layout = inspected["__layout__"]

        name = layout.name

        fqn = name

        if not inspected.get("__doc__"):
            raise HnhmError(
                f"Doc not found or empty for link: '{fqn}'."
                " Please, write a documentation for your link."
            )
        doc: str = inspected["__doc__"]

        if not inspected.get("__keys__"):
            raise HnhmError(
                f"At least one Key is required for '{fqn}'."
                " Please, specify link's keys via the '__keys__' attribute."
            )
        keys_hnhm: list[HnhmEntity] = inspected["__keys__"]
        keys = [key.to_core() for key in keys_hnhm]

        elements = []
        for class_attribute in inspected.values():
            if not isinstance(class_attribute, HnhmLinkElement):
                continue
            link_element = class_attribute.to_core()
            elements.append(link_element)

        if len(elements) < 2:
            raise HnhmError(
                f"At least two LinkElements are required for '{fqn}'."
                " Please, specify more than one elements."
            )

        return Link(
            fqn=fqn,
            name=name,
            layout=layout,
            doc=doc,
            elements=elements,
            keys=keys,
        )
