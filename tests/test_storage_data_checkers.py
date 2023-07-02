from typing import Callable
from dataclasses import field, dataclass

import pytest

from hnhm.core import HnhmError, HnhmStateData
from tests.__hnhm__ import UserWith1Key, UserWith1Key1Group, UserWith1Key1Attribute

state_data = HnhmStateData(entities={}, entities_views=set(), links={})


@dataclass
class Case:
    checker: Callable
    checker_args: tuple[str, ...]
    error: str
    entities: dict = field(default_factory=dict)
    links: dict = field(default_factory=dict)


CASES = [
    Case(
        checker=state_data.check_entity_exists,
        checker_args=("user",),
        error=f"Entity 'user' doesn't exist.",
    ),
    Case(
        checker=state_data.check_entity_not_exists,
        checker_args=("user",),
        error=f"Entity 'user' already exists.",
        entities={"user": None},
    ),
    Case(
        checker=state_data.check_link_exists,
        checker_args=("user_review",),
        error=f"Link 'user_review' doesn't exist.",
    ),
    Case(
        checker=state_data.check_link_not_exists,
        checker_args=("user_review",),
        error=f"Link 'user_review' already exists.",
        links={"user_review": None},
    ),
    Case(
        checker=state_data.check_attribute_exists,
        checker_args=("user", "age"),
        error=f"Attribute 'age' doesn't exist.",
        entities={"user": UserWith1Key().to_core()},
    ),
    Case(
        checker=state_data.check_attribute_not_exists,
        checker_args=("user", "age"),
        error=f"Attribute 'age' already exists.",
        entities={"user": UserWith1Key1Attribute().to_core()},
    ),
    Case(
        checker=state_data.check_group_exists,
        checker_args=("user", "name"),
        error=f"Group 'name' doesn't exist.",
        entities={"user": UserWith1Key().to_core()},
    ),
    Case(
        checker=state_data.check_group_not_exists,
        checker_args=("user", "name"),
        error=f"Group 'name' already exists.",
        entities={"user": UserWith1Key1Group().to_core()},
    ),
    Case(
        checker=state_data.check_group_attribute_exists,
        checker_args=("user", "name", "age"),
        error=f"Attribute 'age' doesn't exist.",
        entities={"user": UserWith1Key1Group().to_core()},
    ),
    Case(
        checker=state_data.check_group_attribute_not_exists,
        checker_args=("user", "name", "first_name"),
        error=f"Attribute 'first_name' already exists.",
        entities={"user": UserWith1Key1Group().to_core()},
    ),
]


@pytest.mark.parametrize("case", CASES)
def test_checker(case: Case):
    state_data.entities = case.entities
    state_data.links = case.links

    with pytest.raises(HnhmError, match=case.error):
        case.checker(*case.checker_args)
