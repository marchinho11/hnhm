import pytest
from click.testing import CliRunner

import hnhm.cli as hnhm_cli
from tests.__hnhm__ import (
    UserWith1Key,
    ReviewWith1Key,
    StageWith5Columns,
    LinkUserReviewWith2Keys,
)


@pytest.fixture
def cli_runner() -> CliRunner:
    runner = CliRunner()
    with runner.isolated_filesystem():
        yield runner


def test_import_registry():
    registry = hnhm_cli.import_registry("tests")
    assert registry


def test_import_registry_failed():
    with pytest.raises(
        ModuleNotFoundError,
        match="No module named 'tests.util.__hnhm__'; 'tests.util' is not a package",
    ):
        hnhm_cli.import_registry("tests.util")


def test_plan(cli_runner):
    result = cli_runner.invoke(hnhm_cli.cli, ["plan", "tests"])
    assert result.exit_code == 0


def test_apply(cli_runner):
    result = cli_runner.invoke(hnhm_cli.cli, ["apply", "-y", "tests"])
    assert result.exit_code == 0


def test_print_plan(hnhm):
    """Just test it prints the plan without checking the output."""
    with hnhm:
        plan = hnhm.plan(
            entities=[ReviewWith1Key(), StageWith5Columns(), UserWith1Key()],
            links=[LinkUserReviewWith2Keys()],
        )
        hnhm_cli.print_plan(plan)
        hnhm.apply(plan)

    with hnhm:
        plan = hnhm.plan(entities=[], links=[])
        hnhm_cli.print_plan(plan)
        hnhm.apply(plan)
