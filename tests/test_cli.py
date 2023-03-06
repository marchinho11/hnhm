import pytest
from click.testing import CliRunner

import hnhm.cli as hnhm_cli
from hnhm import HnhmError
from tests.dwh import User, Stage, Review, UserReview


@pytest.fixture
def cli_runner() -> CliRunner:
    runner = CliRunner()
    with runner.isolated_filesystem():
        yield runner


def test_import_registry():
    registry = hnhm_cli.import_registry("tests.dwh")
    assert registry


def test_import_registry_failed():
    with pytest.raises(
        HnhmError,
        match=(
            f"Failed to import registry from module: 'tests.util'."
            " Please, specify your registry via __registry__ object in your DWH module."
        ),
    ):
        hnhm_cli.import_registry("tests.util")


def test_plan(cli_runner):
    result = cli_runner.invoke(hnhm_cli.cli, ["plan", "tests.dwh"])
    assert result.exit_code == 0


def test_apply(cli_runner):
    result = cli_runner.invoke(hnhm_cli.cli, ["apply", "-y", "tests.dwh"])
    assert result.exit_code == 0


def test_print_plan(hnhm):
    """Just test it prints the plan without checking the output."""
    with hnhm:
        plan = hnhm.plan(entities=[Review(), Stage(), User()], links=[UserReview()])
        hnhm_cli.print_plan(plan)
        hnhm.apply(plan)

    with hnhm:
        plan = hnhm.plan(entities=[], links=[])
        hnhm_cli.print_plan(plan)
        hnhm.apply(plan)
