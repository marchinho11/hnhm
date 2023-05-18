from enum import Enum

import click
import pydantic

from .hnhm import Plan, PlanType
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
    RemoveEntityView,
    AddGroupAttribute,
    RecreateEntityView,
    RemoveGroupAttribute,
)


class Color(str, Enum):
    green = "green"
    red = "red"
    yellow = "yellow"


class PlanLine(pydantic.BaseModel):
    text: str
    color: str | None = None


def lines_from_plan(plan: Plan) -> list[PlanLine]:
    lines = []
    if plan.is_empty():
        lines.append(PlanLine(text="Your DWH is up to date.", color=Color.green))
        return lines

    entities_migrations = sorted(plan.entities_migrations.items(), key=lambda kv: kv[0])
    links_migrations = sorted(plan.links_migrations.items(), key=lambda kv: kv[0])

    lines.append(PlanLine(text="Plan:"))
    for entity_name, plan_collection in entities_migrations:
        if plan_collection.type == PlanType.CREATE:
            symbol, color = "+", Color.green
        elif plan_collection.type == PlanType.REMOVE:
            symbol, color = "-", Color.red
        elif plan_collection.type == PlanType.UPDATE:
            symbol, color = "[u]", Color.yellow
        else:
            raise HnhmError()

        lines.append(PlanLine(text=""))
        lines.append(PlanLine(text=f"{symbol} entity '{entity_name}'", color=color))
        for entity_migration in plan_collection.migrations:
            match entity_migration:
                case CreateEntity(entity=entity):
                    if entity.layout.type == LayoutType.HNHM:
                        lines.append(
                            PlanLine(text=f"  + hub '{entity.name}'", color=Color.green)
                        )
                    else:
                        lines.append(
                            PlanLine(text=f"  + stage '{entity.name}'", color=Color.green)
                        )
                        for attribute in entity.attributes.values():
                            lines.append(
                                PlanLine(
                                    text=f"    |attribute '{attribute.name}'",
                                    color=Color.green,
                                )
                            )

                case RecreateEntityView(entity=entity):
                    lines.append(
                        PlanLine(text=f"  {symbol} view '{entity.name}'", color=color)
                    )

                case CreateAttribute(entity=_, attribute=attribute):
                    lines.append(
                        PlanLine(
                            text=f"  + attribute '{attribute.name}'", color=Color.green
                        )
                    )

                case CreateGroup(entity=_, group=group):
                    lines.append(
                        PlanLine(text=f"  + group '{group.name}'", color=Color.green)
                    )
                    for attribute in group.attributes.values():
                        lines.append(
                            PlanLine(
                                text=f"    |attribute '{attribute.name}'",
                                color=Color.green,
                            )
                        )

                case AddGroupAttribute(entity=_, group=group, attribute=attribute):
                    lines.append(
                        PlanLine(text=f"  [u] group '{group.name}'", color=Color.yellow)
                    )
                    lines.append(
                        PlanLine(
                            text=f"    +attribute '{attribute.name}'", color=Color.green
                        )
                    )

                case RemoveEntity(entity=entity):
                    if entity.layout.type == LayoutType.HNHM:
                        lines.append(
                            PlanLine(text=f"  - hub '{entity.name}'", color=Color.red)
                        )
                    else:
                        lines.append(
                            PlanLine(text=f"  - stage '{entity.name}'", color=Color.red)
                        )
                        for attribute in entity.attributes.values():
                            lines.append(
                                PlanLine(
                                    text=f"    |attribute '{attribute.name}'",
                                    color=Color.red,
                                )
                            )

                case RemoveEntityView(entity=entity):
                    if plan_collection.type == PlanType.REMOVE:
                        lines.append(
                            PlanLine(text=f"  - view '{entity.name}'", color=Color.red)
                        )

                case RemoveAttribute(entity=_, attribute=attribute):
                    lines.append(
                        PlanLine(
                            text=f"  - attribute '{attribute.name}'", color=Color.red
                        )
                    )

                case RemoveGroup(entity=_, group=group):
                    lines.append(
                        PlanLine(text=f"  - group '{group.name}'", color=Color.red)
                    )
                    for attribute in group.attributes.values():
                        lines.append(
                            PlanLine(
                                text=f"    | attribute '{attribute.name}'",
                                color=Color.red,
                            )
                        )

                case RemoveGroupAttribute(entity=_, group=group, attribute=attribute):
                    lines.append(
                        PlanLine(text=f"  [u] group '{group.name}'", color=Color.yellow)
                    )
                    lines.append(
                        PlanLine(
                            text=f"    -attribute '{attribute.name}'", color=Color.red
                        )
                    )

    for link_name, plan_collection in links_migrations:
        if plan_collection.type == PlanType.CREATE:
            symbol, color = "+", Color.green
        elif plan_collection.type == PlanType.REMOVE:
            symbol, color = "-", Color.red
        else:
            raise HnhmError()

        lines.append(PlanLine(text=""))
        lines.append(PlanLine(text=f"{symbol} link '{link_name}'", color=color))
        for link_migration in plan_collection.migrations:
            match link_migration:
                case RemoveLink(link=link):
                    for element in link.elements:
                        lines.append(
                            PlanLine(
                                text=f"  |element '{element.entity.name}'", color=color
                            )
                        )
                case CreateLink(link=link):
                    for element in link.elements:
                        lines.append(
                            PlanLine(
                                text=f"  |element '{element.entity.name}'", color=color
                            )
                        )

    lines.append(PlanLine(text=""))

    return lines


def print_plan(plan: Plan):
    lines = lines_from_plan(plan)
    for line in lines:
        click.secho(line.text, fg=line.color)
