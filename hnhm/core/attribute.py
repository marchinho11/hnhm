from enum import Enum

import pydantic


class Type(str, Enum):
    """Attribute type."""

    STRING = "STRING"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    TIMESTAMP = "TIMESTAMP"

    def __str__(self):
        return self.name


class ChangeType(str, Enum):
    """
    Attribute change type.
      + IGNORE: insert the latest data by business time, ignore updates.
      + UPDATE: insert the latest data by business time, update if business time.
      + NEW: save the full history of changes using SCD2.
    """

    IGNORE = "IGNORE"
    UPDATE = "UPDATE"
    NEW = "NEW"

    def __str__(self):
        return self.name


class Attribute(pydantic.BaseModel):
    """Attribute core representation."""

    name: str
    entity_name: str
    comment: str
    type: Type
    change_type: ChangeType
    group: str | None = None

    @property
    def table(self):
        return f"attr__{self.entity_name}__{self.name}"

    def __str__(self):
        return f"<{self.type} '{self.name}' change_type='{self.change_type}'>"

    def __hash__(self):
        return hash(self.table)

    def __eq__(self, other):
        return hash(self) == hash(other)
