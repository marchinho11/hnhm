import abc
import inspect

from .hnhm_attribute import HnhmAttribute
from .core import Group, Entity, Layout, HnhmError, ChangeType, LayoutType


class HnhmEntity(abc.ABC):
    __layout__: Layout = None
    __keys__: list[HnhmAttribute] | None = None

    def to_core(self) -> Entity:
        inspected = dict(inspect.getmembers(self))

        if not inspected.get("__layout__"):
            raise HnhmError(
                f"Layout not found for entity: '{self}'."
                " Please, specify Layout via '__layout__' attribute."
            )
        layout: Layout = inspected["__layout__"]
        if not layout.type:
            raise HnhmError(
                f"Type for Layout '{layout}' is required for entity."
                " Please, specify LayoutType via 'type' attribute."
            )

        name = layout.name

        fqn = f"{layout.type}.{name}"

        if not inspected.get("__doc__"):
            raise HnhmError(
                f"Doc not found or empty for entity: '{fqn}'."
                " Please, write a documentation for your entity."
            )
        doc: str = inspected["__doc__"]

        match layout.type:
            case LayoutType.STAGE:
                keys = []

            case LayoutType.HNHM:
                if not inspected.get("__keys__"):
                    raise HnhmError(
                        f"At least one Key is required for entity '{fqn}'."
                        " Please, specify entity's keys via the '__keys__' attribute."
                    )

                keys_hnhm: list[HnhmAttribute] = inspected["__keys__"]
                for key in keys_hnhm:
                    if key.change_type != ChangeType.IGNORE:
                        raise HnhmError(
                            f"Change type='{key.change_type}' is not supported for Key attributes."
                            f" Use 'ChangeType.IGNORE' for the key attributes in the '{fqn}' entity."
                        )

                keys = [key.to_core(name) for key in keys_hnhm]
                if len(keys) != len(set(keys)):
                    raise HnhmError(
                        f"Found duplicated keys for entity: '{layout.type}.{name}'."
                    )

            case _:
                raise HnhmError(f"Unknown LayoutType='{layout.type}'")

        groups = {}
        attributes = {}
        for class_attribute in inspected.values():
            if not isinstance(class_attribute, HnhmAttribute):
                continue

            attribute = class_attribute.to_core(name)
            attribute_name = attribute.name

            if attribute.group:
                group_name = attribute.group
                if group_name not in groups:
                    groups[group_name] = Group(
                        name=group_name,
                        entity_name=name,
                        attributes={attribute_name: attribute},
                        change_type=attribute.change_type,
                    )

                if groups[group_name].change_type != attribute.change_type:
                    raise HnhmError(
                        f"Found conflicting ChangeType for the entity='{fqn}' group='{group_name}'."
                        " Please, use single ChangeType for all attributes within the same group."
                    )
                groups[group_name].attributes[attribute_name] = attribute

            elif attribute not in keys:
                attributes[attribute_name] = attribute

        if layout.type == LayoutType.STAGE and len(attributes) < 1:
            raise HnhmError(f"Entity='{fqn}' should have at least 1 attribute.")

        return Entity(
            fqn=fqn,
            name=name,
            layout=layout,
            doc=doc,
            keys=keys,
            attributes=attributes,
            groups=groups,
        )
