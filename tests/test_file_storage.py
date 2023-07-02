import os
import pathlib
from datetime import datetime

import pytest

from hnhm import FileState
from tests.__hnhm__ import UserWith1Key1Group


@pytest.fixture
def file_state_test_file() -> str:
    file_path = "/tmp/" + datetime.now().strftime("%y%m%d_%H%M%S") + ".json"
    yield file_path
    if pathlib.Path(file_path).is_file():
        os.remove(file_path)


def test_file_state(file_state_test_file):
    state = FileState(file_state_test_file)
    data = state.load()
    assert not data.links and not data.entities

    data.entities["user"] = UserWith1Key1Group().to_core()
    state.save(data)

    data = FileState(file_state_test_file).load()
    assert data.entities
    assert not data.links
