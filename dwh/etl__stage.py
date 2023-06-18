from dwh.__hnhm__ import sql


def stage():
    sql.execute(
        """
        INSERT INTO stg__listing(
            id,
            name,
            slug,
            usd_price,
            timestamp
        )
        SELECT
            (data -> 'listing' ->> 'id')::INT                                     AS id,
            data -> 'listing' ->> 'name'                                          AS name,
            data -> 'listing' ->> 'slug'                                          AS slug,
            (data -> 'listing' -> 'quote' -> 'USD' ->> 'price')::DOUBLE PRECISION AS usd_price,
            (data ->> 'timestamp')::timestamptz                                   AS timestamp
        FROM
            raw_listings
        WHERE
            (data ->> 'timestamp')::timestamptz > (
                SELECT COALESCE(MAX(timestamp), '-infinity')
                FROM stg__listing
            );
    """
    )


if __name__ == "__main__":
    stage()
