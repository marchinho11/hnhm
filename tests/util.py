import hashlib
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import Engine, inspect

from hnhm import HnHm, HnhmLink, HnhmEntity

TIME = datetime(2022, 12, 1, 0, 0, 0, 0, tzinfo=timezone.utc)
TIME_INFINITY = datetime(9999, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc)


def md5(*s) -> str:
    return hashlib.md5("-".join(s).encode()).hexdigest()


def insert_data(data: dict, table: str, engine: Engine):
    df = pd.DataFrame(data)
    df.to_sql(table, con=engine, if_exists="append", index=False)
    engine.dispose()


def get_data(table: str, engine: Engine, sort_by: list[str] | None = None) -> dict:
    df = pd.read_sql_query(f"SELECT * FROM {table}", con=engine)
    if sort_by:
        df = df.sort_values(sort_by)
    engine.dispose()
    return df.to_dict(orient="list")


def init_dwh(
    *,
    stage_data: dict[str, dict],
    hnhm: HnHm,
    engine: Engine,
    entities: list[HnhmEntity] | None = None,
    links: list[HnhmLink] | None = None,
):
    if entities or links:
        with hnhm:
            hnhm.apply(hnhm.plan(entities=entities, links=links))

    for stage_table_name, data in stage_data.items():
        insert_data(data, stage_table_name, engine)


def get_tables_in_database(engine: Engine) -> set[str]:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    engine.dispose()
    return table_names
