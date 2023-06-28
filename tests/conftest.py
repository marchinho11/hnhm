import os
import random
import string

import pytest
import psycopg2

from hnhm.core.state import InMemState
from hnhm import HnHm, PostgresPsycopgSql

PG_USER = os.getenv("PG_USER", "mark")

# Used only to create database with random name for tests
PG_DB = os.getenv("PG_DB", "template1")


def generate_random_db_name(size=16, chars=string.ascii_lowercase):
    random_chars = "".join(random.choice(chars) for _ in range(size))
    return f"hnhm_test_{random_chars}"


@pytest.fixture
def postgres_db() -> str:
    random_db_name = generate_random_db_name()

    connection = psycopg2.connect(database=PG_DB, user=PG_USER, host="localhost", port=5432)
    connection.autocommit = True

    cursor = connection.cursor()
    try:
        cursor.execute(f"CREATE DATABASE {random_db_name}")
        yield random_db_name
    finally:
        cursor.execute(f"DROP DATABASE IF EXISTS {random_db_name}")

        cursor.close()
        connection.close()


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
def cursor(postgres_db):
    connection = psycopg2.connect(database=postgres_db, user=PG_USER, host="localhost", port=5432)
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        yield cursor
    finally:
        cursor.close()
        connection.close()
