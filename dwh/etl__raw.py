import requests
from psycopg2.extras import Json

from dwh.__hnhm__ import sql

COINMARKET_TOKEN = "<TOKEN>"


def get_listings() -> list[dict]:
    r = requests.get(
        "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest",
        headers={"X-CMC_PRO_API_KEY": COINMARKET_TOKEN},
    )
    assert r.status_code == 200

    data = r.json()

    return [
        {"timestamp": data["status"]["timestamp"], "listing": listing}
        for listing in data["data"]
    ]


def save_listings(listings: list[dict]):
    sql.execute(
        """
        CREATE TABLE IF NOT EXISTS raw_listings(
            id SERIAL PRIMARY KEY,
            data JSONB
        )
    """
    )

    sql.execute_many(
        """
        INSERT INTO
            raw_listings(data)
        VALUES
            (%s)
    """,
        ((Json(listing),) for listing in listings),
    )


if __name__ == "__main__":
    listings = get_listings()

    save_listings(listings)
