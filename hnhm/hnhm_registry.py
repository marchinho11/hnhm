from .hnhm import HnHm
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
        self.hnhm = hnhm
        self.entities = entities
        self.links = links

    def __str__(self):
        return "<HnhmRegistry>"
