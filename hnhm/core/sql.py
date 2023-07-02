import abc

from .task import Task
from .migration import Migration


class Sql(abc.ABC):
    """Generates and executes sql code."""

    @abc.abstractmethod
    def generate_sql(self, migration_or_task: Migration | Task) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def execute(self, sql: str):
        raise NotImplementedError

    @abc.abstractmethod
    def execute_many(self, sql: str, values: list):
        raise NotImplementedError


class FakeSql(Sql):
    def generate_sql(self, migration_or_task: Migration | Task) -> str:
        return ""

    def execute(self, sql: str):
        pass

    def execute_many(self, sql: str, values: list):
        pass
