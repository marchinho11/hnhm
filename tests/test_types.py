from tests.util import get_tables, get_columns_with_types
from hnhm import (
    Float,
    Layout,
    String,
    Boolean,
    Integer,
    Timestamp,
    ChangeType,
    HnhmEntity,
    LayoutType,
)


class Types(HnhmEntity):
    """Tests for different types."""

    __layout__ = Layout(name="types", type=LayoutType.HNHM)
    string = String(comment="String", change_type=ChangeType.IGNORE)
    float = Float(comment="Float", change_type=ChangeType.IGNORE, group="types")
    integer = Integer(comment="Integer", change_type=ChangeType.IGNORE, group="types")
    boolean = Boolean(comment="Boolean", change_type=ChangeType.IGNORE, group="types")
    timestamp = Timestamp(
        comment="Timestamp", change_type=ChangeType.IGNORE, group="types"
    )
    __keys__ = [string]


def test_types(hnhm, cursor):
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[Types()]))

    assert get_tables(cursor) == {"hub__types", "group__types__types"}
    assert get_columns_with_types("hub__types", cursor) == {
        "_loaded_at": "timestamp with time zone",
        "_source": "character varying",
        "string_bk": "text",
        "types_sk": "character varying",
        "valid_from": "timestamp with time zone",
    }
    assert get_columns_with_types("group__types__types", cursor) == {
        "_hash": "character varying",
        "_loaded_at": "timestamp with time zone",
        "_source": "character varying",
        "boolean": "boolean",
        "float": "double precision",
        "integer": "integer",
        "timestamp": "timestamp with time zone",
        "types_sk": "character varying",
        "valid_from": "timestamp with time zone",
    }
