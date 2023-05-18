import os
import random
import string

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy import text, create_engine

from hnhm import HnHm, InMemStorage, PostgresSqlalchemySql

# Used only to create database with random name for tests
PG_DB = os.getenv("PG_DB", "hnhm")
PG_USER = os.getenv("PG_USER", "mark")


def generate_random_db_name(size=16, chars=string.ascii_lowercase):
    random_chars = "".join(random.choice(chars) for _ in range(size))
    return f"hnhm_test_{random_chars}"


@pytest.fixture
def sqlalchemy_engine() -> Engine:
    random_db_name = generate_random_db_name()

    engine = create_engine(f"postgresql+psycopg2://{PG_USER}@localhost/{PG_DB}")
    conn = engine.connect()
    conn = conn.execution_options(isolation_level="AUTOCOMMIT")
    conn.execute(text(f"CREATE DATABASE {random_db_name}"))

    yield create_engine(f"postgresql+psycopg2://{PG_USER}@localhost/{random_db_name}")

    conn.execute(text(f"DROP DATABASE {random_db_name}"))
    conn.close()
    engine.dispose()


@pytest.fixture
def hnhm(sqlalchemy_engine) -> HnHm:
    yield HnHm(
        sql=PostgresSqlalchemySql.with_engine(sqlalchemy_engine),
        storage=InMemStorage(),
    )
