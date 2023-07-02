from hnhm import Float, Layout, String, Integer, ChangeType, HnhmEntity, LayoutType


class Listing(HnhmEntity):
    """Listing for the CoinMarket API."""

    __layout__ = Layout(name="listing", type=LayoutType.HNHM)

    id = Integer(
        comment="ID the Crypto Currency in the CoinMarket API.",
        change_type=ChangeType.IGNORE,
    )
    slug = String(
        comment="Slug of the Crypto Currency. For example: 'bitcoin'.",
        change_type=ChangeType.NEW,
        group="name",
    )
    name = String(
        comment="Name of the Crypto Currency. For example: 'Bitcoin'.",
        change_type=ChangeType.NEW,
        group="name",
    )
    usd_price = Float(
        comment="USD Price.",
        change_type=ChangeType.NEW,
    )

    __keys__ = [id]
