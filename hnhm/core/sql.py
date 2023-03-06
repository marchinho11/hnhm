import abc

from .tasks import Task
from .mutations import Mutation


class Sql(abc.ABC):
    """Generates and executes sql code."""

    @abc.abstractmethod
    def generate_sql(self, mutation_or_task: Mutation | Task) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def execute(self, sql: str):
        raise NotImplementedError


class FakeSql(Sql):
    def generate_sql(self, mutation_or_task: Mutation | Task) -> str:
        return ""

    def execute(self, sql: str):
        pass
