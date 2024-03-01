import os
import random
import string

import pytest
import psycopg
from psycopg import Cursor

from hnhm.core.state import InMemState
from hnhm import HnHm, PostgresPsycopgSql

PG_HOST = "localhost"
PG_USER = os.getenv("PG_USER", "mark")

# Used only to create database with random name for tests
PG_DB = os.getenv("PG_DB", "template1")


def generate_random_db_name(size=16, chars=string.ascii_lowercase):
    random_chars = "".join(random.choice(chars) for _ in range(size))
    return f"hnhm_test_{random_chars}"


@pytest.fixture
def postgres_db() -> str:
    random_db_name = generate_random_db_name()

    try:
        with psycopg.connect(
            dbname=PG_DB, user=PG_USER, host=PG_HOST, autocommit=True
        ) as conn:
            conn.execute(f"CREATE DATABASE {random_db_name}")
        yield random_db_name
    finally:
        with psycopg.connect(
            dbname=PG_DB, user=PG_USER, host=PG_HOST, autocommit=True
        ) as conn:
            conn.execute(f"DROP DATABASE IF EXISTS {random_db_name}")


@pytest.fixture
def hnhm(postgres_db) -> HnHm:
    yield HnHm(
        sql=PostgresPsycopgSql(
            database=postgres_db,
            user=PG_USER,
        ),
        state=InMemState(),
    )


@pytest.fixture
def cursor(postgres_db) -> Cursor:
    with psycopg.connect(
        dbname=postgres_db, user=PG_USER, host=PG_HOST, autocommit=True
    ) as conn:
        with conn.cursor() as cur:
            yield cur
