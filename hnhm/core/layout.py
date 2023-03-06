from enum import Enum

import pydantic


class LayoutType(str, Enum):
    """
    Layout type.
      + STAGE: create single table with all provided attributes.
      + HNHM: create hub, attributes, and group tables.
    """

    STAGE = "STAGE"
    HNHM = "HNHM"

    def __str__(self):
        return self.name


class Layout(pydantic.BaseModel):
    """Layout core representation for entities and links."""

    name: str
    type: LayoutType | None = None

    def __str__(self):
        return f"<Layout '{self.name}' type='{self.type}'>"
