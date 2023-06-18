from enum import Enum

import pydantic

from .hnhm_link import HnhmLink
from .hnhm_entity import HnhmEntity
from .core import Sql, State, Entity, HnhmError, LayoutType, migration


class PlanType(str, Enum):
    CREATE = "CREATE"
    REMOVE = "REMOVE"
    UPDATE = "UPDATE"


class PlanCollection(pydantic.BaseModel):
    type: PlanType
    migrations: list[migration.Migration]


class Plan(pydantic.BaseModel):
    entities_migrations: dict[str, PlanCollection]
    links_migrations: dict[str, PlanCollection]

    def is_empty(self):
        return not self.entities_migrations and not self.links_migrations

    @property
    def migrations_all(self):
        migrations: list[migration.Migration] = []

        for collection in self.entities_migrations.values():
            migrations.extend(collection.migrations)

        for collection in self.links_migrations.values():
            migrations.extend(collection.migrations)

        migrations = sorted(migrations, key=lambda m: m.priority)
        return migrations


class HnHm:
    def __init__(self, *, sql: Sql, state: State):
        self.sql = sql
        self.state = state
        self.data = self.state.load()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.state.save(self.data)

    def plan(
        self,
        *,
        entities: list[HnhmEntity] | None = None,
        links: list[HnhmLink] | None = None,
    ) -> Plan:
        core_entities = {}
        for entity in entities or []:
            entity_core = entity.to_core()
            core_entities[entity_core.fqn] = entity_core

        core_links = {}
        for link in links or []:
            link_core = link.to_core()
            core_links[link_core.fqn] = link_core

        plan = Plan(entities_migrations={}, links_migrations={})

        # Entity: create if not exists
        for entity in core_entities.values():
            migrations = []

            # Entity's View: create/update if not exists
            if (
                entity.fqn not in self.data.entities_views
                and entity.layout.type == LayoutType.HNHM
            ):
                migrations.append(migration.RecreateEntityView(entity=entity))

            # Create Entity
            if entity.fqn not in self.data.entities:
                migrations.append(migration.CreateEntity(entity=entity))

                if entity.layout.type == LayoutType.HNHM:
                    # Create Attribute
                    for attribute in entity.attributes.values():
                        migrations.append(
                            migration.CreateAttribute(entity=entity, attribute=attribute)
                        )
                    # Create Group
                    for group in entity.groups.values():
                        migrations.append(
                            migration.CreateGroup(entity=entity, group=group)
                        )

            if migrations:
                plan.entities_migrations[entity.fqn] = PlanCollection(
                    type=PlanType.CREATE,
                    migrations=migrations,
                )

        # Entity: create/remove/update Attribute/Group
        for entity in core_entities.values():
            if entity.fqn not in self.data.entities:
                continue

            attributes_state = self.data.entities[entity.fqn].attributes
            groups_state = self.data.entities[entity.fqn].groups

            migrations = []
            # Create Attribute
            for attribute_name, attribute in entity.attributes.items():
                if attribute_name not in attributes_state:
                    migrations.append(
                        migration.CreateAttribute(entity=entity, attribute=attribute)
                    )

            # Remove Attribute
            for attribute_name, attribute in attributes_state.items():
                if attribute_name not in entity.attributes:
                    migrations.append(
                        migration.RemoveAttribute(entity=entity, attribute=attribute)
                    )

            # Create/Update Group
            for group_name, group in entity.groups.items():
                # Update
                if group_name in groups_state:
                    group_state = groups_state[group_name]
                    # Add an Attribute to a Group
                    for attribute_name, attribute in group.attributes.items():
                        if attribute_name not in group_state.attributes:
                            migrations.append(
                                migration.AddGroupAttribute(
                                    entity=entity, group=group, attribute=attribute
                                )
                            )
                    # Remove an Attribute from a Group
                    for attribute_name, attribute in group_state.attributes.items():
                        if attribute_name not in group.attributes:
                            migrations.append(
                                migration.RemoveGroupAttribute(
                                    entity=entity, group=group, attribute=attribute
                                )
                            )
                # Create
                else:
                    migrations.append(migration.CreateGroup(entity=entity, group=group))

            # Remove Group
            for group_name, group in groups_state.items():
                if group_name not in entity.groups:
                    migrations.append(migration.RemoveGroup(entity=entity, group=group))

            if migrations:
                if entity.layout.type == LayoutType.HNHM:
                    migrations.extend(
                        [
                            migration.RemoveEntityView(entity=entity),
                            migration.RecreateEntityView(entity=entity),
                        ]
                    )
                plan.entities_migrations[entity.fqn] = PlanCollection(
                    type=PlanType.UPDATE,
                    migrations=migrations,
                )

        # Link: remove
        for link_name, link in self.data.links.items():
            if link_name not in core_links:
                plan.links_migrations[link_name] = PlanCollection(
                    type=PlanType.REMOVE,
                    migrations=[migration.RemoveLink(link=link)],
                )

        # Entity: remove
        for entity_name, entity in self.data.entities.items():
            if entity_name not in core_entities:
                migrations = []

                if entity.layout.type == LayoutType.HNHM:
                    migrations.append(migration.RemoveEntityView(entity=entity))

                    attributes_state = self.data.entities[entity_name].attributes
                    groups_state = self.data.entities[entity_name].groups
                    # Remove Attribute
                    for _, attribute_state in attributes_state.items():
                        migrations.append(
                            migration.RemoveAttribute(
                                entity=entity, attribute=attribute_state
                            )
                        )
                    # Remove Group
                    for group_name, group in groups_state.items():
                        migrations.append(
                            migration.RemoveGroup(entity=entity, group=group)
                        )

                migrations.append(migration.RemoveEntity(entity=entity))
                plan.entities_migrations[entity_name] = PlanCollection(
                    type=PlanType.REMOVE,
                    migrations=migrations,
                )

        # Link: create
        for link_name, link in core_links.items():
            if link_name not in self.data.links:
                plan.links_migrations[link.fqn] = PlanCollection(
                    type=PlanType.CREATE,
                    migrations=[migration.CreateLink(link=link)],
                )

        return plan

    def apply(self, plan: Plan):
        for plan_migration in plan.migrations_all:
            sql = self.sql.generate_sql(plan_migration)

            match plan_migration:
                case migration.CreateEntity(entity=entity):
                    self.data.check_entity_not_exists(entity.fqn)
                    self.sql.execute(sql)
                    if entity.layout.type == LayoutType.HNHM:
                        attributes = {}
                        groups = {}
                    else:
                        attributes = entity.attributes
                        groups = entity.groups
                    self.data.entities[entity.fqn] = Entity(
                        fqn=entity.fqn,
                        name=entity.name,
                        layout=entity.layout,
                        doc=entity.doc,
                        keys=entity.keys,
                        attributes=attributes,
                        groups=groups,
                    )

                case migration.RemoveEntity(entity=entity):
                    self.data.check_entity_exists(entity.fqn)
                    self.sql.execute(sql)
                    del self.data.entities[entity.fqn]

                case migration.RecreateEntityView(entity=entity):
                    self.sql.execute(sql)
                    self.data.entities_views.add(entity.fqn)

                case migration.RemoveEntityView(entity=entity):
                    if entity.fqn not in self.data.entities_views:
                        raise HnhmError(f"Entity's View '{entity.fqn}' doesn't exist.")
                    self.sql.execute(sql)
                    self.data.entities_views.remove(entity.fqn)

                case migration.CreateAttribute(entity=entity, attribute=attribute):
                    self.data.check_attribute_not_exists(entity.fqn, attribute.name)
                    self.sql.execute(sql)
                    self.data.entities[entity.fqn].attributes[attribute.name] = attribute

                case migration.RemoveAttribute(entity=entity, attribute=attribute):
                    self.data.check_attribute_exists(entity.fqn, attribute.name)
                    self.sql.execute(sql)
                    del self.data.entities[entity.fqn].attributes[attribute.name]

                case migration.CreateGroup(entity=entity, group=group):
                    self.data.check_group_not_exists(entity.fqn, group.name)
                    self.sql.execute(sql)
                    self.data.entities[entity.fqn].groups[group.name] = group

                case migration.RemoveGroup(entity=entity, group=group):
                    self.data.check_group_exists(entity.fqn, group.name)
                    self.sql.execute(sql)
                    del self.data.entities[entity.fqn].groups[group.name]

                case migration.AddGroupAttribute(
                    entity=entity, group=group, attribute=attribute
                ):
                    self.data.check_group_attribute_not_exists(
                        entity.fqn, group.name, attribute.name
                    )
                    self.sql.execute(sql)
                    self.data.entities[entity.fqn].groups[group.name].attributes[
                        attribute.name
                    ] = attribute

                case migration.RemoveGroupAttribute(
                    entity=entity, group=group, attribute=attribute
                ):
                    self.data.check_group_attribute_exists(
                        entity.fqn, group.name, attribute.name
                    )
                    self.sql.execute(sql)
                    del (
                        self.data.entities[entity.fqn]
                        .groups[group.name]
                        .attributes[attribute.name]
                    )

                case migration.CreateLink(link=link):
                    self.data.check_link_not_exists(link.fqn)
                    self.sql.execute(sql)
                    self.data.links[link.fqn] = link

                case migration.RemoveLink(link=link):
                    self.data.check_link_exists(link.fqn)
                    self.sql.execute(sql)
                    del self.data.links[link.fqn]

                case _:
                    raise HnhmError(f"Unknown migration: '{migration}'")
