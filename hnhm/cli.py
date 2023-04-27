import sys
import importlib

import click

from .core import HnhmError
from .plan_printer import print_plan
from .hnhm_registry import HnhmRegistry


def import_registry(module: str) -> HnhmRegistry:
    sys.path.append(".")
    imported_module = importlib.import_module(module)
    registry: HnhmRegistry = getattr(imported_module, "__registry__", None)
    if not registry:
        raise HnhmError(
            f"Failed to import registry from module: '{module}'."
            " Please, specify your registry via __registry__ object in your DWH module."
        )
    return registry


@click.group()
def cli():
    pass


@cli.command()
@click.argument("dwh_module")
def plan(dwh_module: str):
    registry = import_registry(dwh_module)

    with registry.hnhm as hnhm:
        plan = hnhm.plan(entities=registry.entities, links=registry.links)
        print_plan(plan)


@cli.command()
@click.argument("dwh_module")
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    default=False,
    show_default=True,
    help="Apply plan without confirmation.",
)
def apply(dwh_module: str, yes: bool):
    registry = import_registry(dwh_module)

    with registry.hnhm as hnhm:
        plan = hnhm.plan(entities=registry.entities, links=registry.links)
        print_plan(plan)

    if plan.is_empty():
        return

    if yes or click.confirm("Apply migrations?"):
        with registry.hnhm as hnhm:
            hnhm.apply(plan)

        click.secho("Applied!", fg="green")
