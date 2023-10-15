import hashlib
from datetime import datetime, timezone

from psycopg2.extensions import AsIs
from psycopg2.extensions import cursor as Cursor

from hnhm import HnHm, HnhmLink, HnhmEntity

TIME = datetime(
    year=2022,
    month=12,
    day=1,
    hour=0,
    minute=0,
    second=0,
    microsecond=0,
    tzinfo=timezone.utc,
)

TIME_INFINITY = datetime(
    year=9999,
    month=12,
    day=31,
    hour=23,
    minute=59,
    second=59,
    microsecond=999999,
    tzinfo=timezone.utc,
)


def md5(*s) -> str:
    return hashlib.md5("-".join(s).encode()).hexdigest()


def insert_row(table: str, row: dict, cursor):
    columns = ",".join(row.keys())
    values = tuple(row.values())

    cursor.execute(
        f"INSERT INTO {table}(%s) values %s",
        (AsIs(columns), values),
    )


def get_rows(
    table: str,
    cursor,
    exclude_columns: set[str] | None = None,
    order_by: str | None = None,
) -> list[dict]:
    exclude_columns = exclude_columns or {"_loaded_at"}

    sql = f"SELECT * FROM {table}"
    if order_by:
        sql += f" ORDER BY {order_by}"

    cursor.execute(sql)
    rows = cursor.fetchall()
    columns = [d[0] for d in cursor.description]
    dicts = [
        dict(filter(lambda cr: cr[0] not in exclude_columns, zip(columns, row)))
        for row in rows
    ]
    return dicts


def init_dwh(
    *,
    hnhm: HnHm,
    stage_data: dict[str, list],
    cursor,
    entities: list[HnhmEntity] | None = None,
    links: list[HnhmLink] | None = None,
):
    if entities or links:
        with hnhm:
            hnhm.apply(hnhm.plan(entities=entities, links=links))

    for stage_table_name, rows in stage_data.items():
        for row in rows:
            insert_row(stage_table_name, row, cursor)


def get_tables(cursor: Cursor) -> set[str]:
    cursor.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname='public'")
    tables = cursor.fetchall()
    tables = set(t[0] for t in tables)

    return tables


def get_views(cursor: Cursor) -> set[str]:
    cursor.execute("SELECT viewname FROM pg_catalog.pg_views WHERE schemaname='public'")
    views = cursor.fetchall()
    views = set(t[0] for t in views)
    return views


def get_columns(table: str, cursor: Cursor) -> set[str]:
    cursor.execute(
        f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'"
    )
    columns = cursor.fetchall()
    columns = set(c[0] for c in columns)
    return columns


def get_columns_with_types(table: str, cursor: Cursor) -> dict[str, str]:
    cursor.execute(
        f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}'"
    )
    columns_with_types = dict(cursor.fetchall())
    return columns_with_types
