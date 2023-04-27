from typing import Callable
from dataclasses import field, dataclass

import pytest

from tests.dwh import User
from hnhm import String, ChangeType
from hnhm.core import HnhmError, HnhmStorageData

storage_data = HnhmStorageData(entities={}, links={})


class UserWithAttribute(User):
    """UserWithAttribute."""

    name = String(comment="Name.", change_type=ChangeType.IGNORE)


class UserWithGroup(User):
    """UserWithGroup."""

    name = String(comment="User name", change_type=ChangeType.IGNORE, group="user_data")


@dataclass
class Case:
    checker: Callable
    checker_args: tuple[str, ...]
    error: str
    entities: dict = field(default_factory=dict)
    links: dict = field(default_factory=dict)


CASES = [
    Case(
        checker=storage_data.check_entity_exists,
        checker_args=("user",),
        error=f"Entity 'user' doesn't exist.",
    ),
    Case(
        checker=storage_data.check_entity_not_exists,
        checker_args=("user",),
        error=f"Entity 'user' already exists.",
        entities={"user": None},
    ),
    Case(
        checker=storage_data.check_link_exists,
        checker_args=("user_review",),
        error=f"Link 'user_review' doesn't exist.",
    ),
    Case(
        checker=storage_data.check_link_not_exists,
        checker_args=("user_review",),
        error=f"Link 'user_review' already exists.",
        links={"user_review": None},
    ),
    Case(
        checker=storage_data.check_attribute_exists,
        checker_args=("user", "age"),
        error=f"Attribute 'age' doesn't exist.",
        entities={"user": User().to_core()},
    ),
    Case(
        checker=storage_data.check_attribute_not_exists,
        checker_args=("user", "name"),
        error=f"Attribute 'name' already exists.",
        entities={"user": UserWithAttribute().to_core()},
    ),
    Case(
        checker=storage_data.check_group_exists,
        checker_args=("user", "user_data"),
        error=f"Group 'user_data' doesn't exist.",
        entities={"user": User().to_core()},
    ),
    Case(
        checker=storage_data.check_group_not_exists,
        checker_args=("user", "user_data"),
        error=f"Group 'user_data' already exists.",
        entities={"user": UserWithGroup().to_core()},
    ),
    Case(
        checker=storage_data.check_group_attribute_exists,
        checker_args=("user", "user_data", "age"),
        error=f"Attribute 'age' doesn't exist.",
        entities={"user": UserWithGroup().to_core()},
    ),
    Case(
        checker=storage_data.check_group_attribute_not_exists,
        checker_args=("user", "user_data", "name"),
        error=f"Attribute 'name' already exists.",
        entities={"user": UserWithGroup().to_core()},
    ),
]


@pytest.mark.parametrize("case", CASES)
def test_checker(case: Case):
    storage_data.entities = case.entities
    storage_data.links = case.links

    with pytest.raises(HnhmError, match=case.error):
        case.checker(*case.checker_args)
