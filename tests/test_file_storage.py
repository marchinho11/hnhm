import os
import pathlib
from datetime import datetime

import pytest

from tests.dwh import User
from hnhm import FileStorage


@pytest.fixture
def file_storage_test_file() -> str:
    file_path = "/tmp/" + datetime.now().strftime("%y%m%d_%H%M%S") + ".json"
    yield file_path
    if pathlib.Path(file_path).is_file():
        os.remove(file_path)


def test_file_storage(file_storage_test_file):
    storage = FileStorage(file_storage_test_file)
    state = storage.load()
    assert not state.links and not state.entities

    state.entities["user"] = User().to_core()
    storage.save(state)

    state = FileStorage(file_storage_test_file).load()
    assert state.entities
    assert not state.links
