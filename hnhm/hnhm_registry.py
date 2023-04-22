from .hnhm import HnHm
from .core import HnhmError
from .hnhm_link import HnhmLink
from .hnhm_entity import HnhmEntity


class HnhmRegistry:
    def __init__(
        self,
        *,
        hnhm: HnHm,
        entities: list[HnhmEntity] | None = None,
        links: list[HnhmLink] | None = None,
    ):
        entities_names = set()
        for entity in entities:
            entity_core = entity.to_core()
            full_entity_name = f"{entity_core.layout.type}.{entity_core.name}"
            if full_entity_name in entities_names:
                raise HnhmError(
                    f"Found duplicated entity: '{full_entity_name}'."
                    " Please, use unique name for each entity and LayoutType."
                )
            entities_names.add(full_entity_name)

        links_names = set()
        for link in links:
            link_core = link.to_core()
            if link_core.name in links_names:
                raise HnhmError(
                    f"Found duplicated link: '{link_core.name}'."
                    " Please, use unique name for each link."
                )
            links_names.add(link_core.name)

        self.hnhm = hnhm
        self.entities = entities
        self.links = links

    def __str__(self):
        return "<HnhmRegistry>"
