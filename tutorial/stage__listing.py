from hnhm import (
    Float,
    Layout,
    String,
    Integer,
    Timestamp,
    ChangeType,
    HnhmEntity,
    LayoutType,
)


class ListingStage(HnhmEntity):
    """Stage data representing a Listing from the CoinMarket API."""

    __layout__ = Layout(name="listing", type=LayoutType.STAGE)

    id = Integer(
        comment="ID the Crypto Currency in the CoinMarket API.",
        change_type=ChangeType.IGNORE,
    )
    slug = String(
        comment="Slug of the Crypto Currency. For example: 'bitcoin'.",
        change_type=ChangeType.IGNORE,
    )
    name = String(
        comment="Name of the Crypto Currency. For example: 'Bitcoin'.",
        change_type=ChangeType.IGNORE,
    )
    usd_price = Float(
        comment="USD Price.",
        change_type=ChangeType.IGNORE,
    )
    timestamp = Timestamp(
        comment="Timestamp when the data was fetched. Comes from data['status']['timestamp'].",
        change_type=ChangeType.IGNORE,
    )
