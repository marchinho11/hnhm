import sys
import importlib

import click

from .hnhm import Plan, PlanType
from .hnhm_registry import HnhmRegistry
from .core import (
    HnhmError,
    CreateLink,
    LayoutType,
    RemoveLink,
    CreateGroup,
    RemoveGroup,
    CreateEntity,
    RemoveEntity,
    CreateAttribute,
    RemoveAttribute,
    AddGroupAttribute,
    RemoveGroupAttribute,
)


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


def print_plan(plan: Plan):
    if plan.is_empty():
        click.secho("Your DWH is up to date.", fg="green")
        return

    entities_mutations = sorted(plan.entities_mutations.items(), key=lambda kv: kv[0])
    links_mutations = sorted(plan.links_mutations.items(), key=lambda kv: kv[0])

    click.secho("Plan:")
    for entity_name, plan_collection in entities_mutations:
        if plan_collection.type == PlanType.CREATE:
            symbol, color = "+", "green"
        elif plan_collection.type == PlanType.REMOVE:
            symbol, color = "-", "red"
        elif plan_collection.type == PlanType.UPDATE:
            symbol, color = "[u]", "yellow"
        else:
            raise HnhmError()

        click.secho(f"\n{symbol} entity '{entity_name}'", fg=color)
        for entity_mutation in plan_collection.mutations:
            match entity_mutation:
                case CreateEntity(entity=entity):
                    if entity.layout.type == LayoutType.HNHM:
                        click.secho(f"  + hub '{entity.name}'", fg="green")
                    else:
                        click.secho(f"  + stage '{entity.name}'", fg="green")
                        for attribute in entity.attributes.values():
                            click.secho(f"    |attribute '{attribute.name}'", fg="green")

                case CreateAttribute(entity=_, attribute=attribute):
                    click.secho(f"  + attribute '{attribute.name}'", fg="green")

                case CreateGroup(entity=_, group=group):
                    click.secho(f"  + group '{group.name}'", fg="green")
                    for attribute in group.attributes.values():
                        click.secho(f"    |attribute '{attribute.name}'", fg="green")

                case AddGroupAttribute(entity=_, group=group, attribute=attribute):
                    click.secho(f"  [u] group '{group.name}'", fg="yellow")
                    click.secho(f"    +attribute '{attribute.name}'", fg="green")

                case RemoveEntity(entity=entity):
                    if entity.layout.type == LayoutType.HNHM:
                        click.secho(f"  - hub '{entity.name}'", fg="red")
                    else:
                        click.secho(f"  - stage '{entity.name}'", fg="red")
                        for attribute in entity.attributes.values():
                            click.secho(f"    |attribute '{attribute.name}'", fg="red")

                case RemoveAttribute(entity=_, attribute=attribute):
                    click.secho(f"  - attribute '{attribute.name}'", fg="red")

                case RemoveGroup(entity=_, group=group):
                    click.secho(f"  - group '{group.name}'", fg="red")
                    for attribute in group.attributes.values():
                        click.secho(f"    | attribute '{attribute.name}'", fg="red")

                case RemoveGroupAttribute(entity=_, group=group, attribute=attribute):
                    click.secho(f"  [u] group '{group.name}'", fg="yellow")
                    click.secho(f"    -attribute '{attribute.name}'", fg="red")

    for link_name, plan_collection in links_mutations:
        if plan_collection.type == PlanType.CREATE:
            symbol, color = "+", "green"
        elif plan_collection.type == PlanType.REMOVE:
            symbol, color = "-", "red"
        elif plan_collection.type == PlanType.UPDATE:
            symbol, color = "[u]", "yellow"
        else:
            raise HnhmError()

        click.secho(f"\n{symbol} link '{link_name}'", fg=color)
        for link_mutation in plan_collection.mutations:
            match link_mutation:
                case RemoveLink(link=link):
                    for element in link.elements:
                        click.secho(f"  |element '{element.entity.name}'", fg=color)
                case CreateLink(link=link):
                    for element in link.elements:
                        click.secho(f"  |element '{element.entity.name}'", fg=color)

    click.secho()


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

    if yes or click.confirm("Apply mutations?"):
        with registry.hnhm as hnhm:
            hnhm.apply(plan)

        click.secho("Applied!", fg="green")
