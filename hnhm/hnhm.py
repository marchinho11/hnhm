from enum import Enum

import pydantic

from hnhm.core import (
    Sql,
    Entity,
    Storage,
    HnhmError,
    Migration,
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

from .hnhm_link import HnhmLink
from .hnhm_entity import HnhmEntity


class PlanType(str, Enum):
    CREATE = "CREATE"
    REMOVE = "REMOVE"
    UPDATE = "UPDATE"


class PlanCollection(pydantic.BaseModel):
    type: PlanType
    migrations: list[Migration]


class Plan(pydantic.BaseModel):
    entities_migrations: dict[str, PlanCollection]
    links_migrations: dict[str, PlanCollection]

    def is_empty(self):
        return not self.entities_migrations and not self.links_migrations

    @property
    def migrations_all(self):
        migrations: list[Migration] = []
        for collection in self.entities_migrations.values():
            migrations.extend(collection.migrations)
        for collection in self.links_migrations.values():
            migrations.extend(collection.migrations)
        migrations = sorted(migrations, key=lambda m: m.priority)
        return migrations


class HnHm:
    def __init__(self, *, sql: Sql, storage: Storage):
        self.sql = sql
        self.storage = storage
        self.data = self.storage.load()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.storage.save(self.data)

    def plan(
        self,
        *,
        entities: list[HnhmEntity] | None = None,
        links: list[HnhmLink] | None = None,
    ) -> Plan:
        core_entities = {}
        for entity in entities or []:
            entity_core = entity.to_core()
            core_entities[entity_core.name] = entity_core

        core_links = {}
        for link in links or []:
            link_core = link.to_core()
            core_links[link_core.name] = link_core

        plan = Plan(entities_migrations={}, links_migrations={})

        # Entity: create if not exists
        for entity in core_entities.values():
            migrations = []

            # Entity's View: create/update if not exists
            if (
                entity.name not in self.data.entities_views
                and entity.layout.type == LayoutType.HNHM
            ):
                migrations.append(RecreateEntityView(entity=entity))

            # Create Entity
            if entity.name not in self.data.entities:
                migrations.append(CreateEntity(entity=entity))

                if entity.layout.type == LayoutType.HNHM:
                    # Create Attribute
                    for attribute in entity.attributes.values():
                        migrations.append(
                            CreateAttribute(entity=entity, attribute=attribute)
                        )
                    # Create Group
                    for group in entity.groups.values():
                        migrations.append(CreateGroup(entity=entity, group=group))

            if migrations:
                plan.entities_migrations[entity.name] = PlanCollection(
                    type=PlanType.CREATE,
                    migrations=migrations,
                )

        # Entity: create/remove/update Attribute/Group
        for entity in core_entities.values():
            if entity.name not in self.data.entities:
                continue

            attributes_state = self.data.entities[entity.name].attributes
            groups_state = self.data.entities[entity.name].groups

            migrations = []
            # Create Attribute
            for attribute_name, attribute in entity.attributes.items():
                if attribute_name not in attributes_state:
                    migrations.append(CreateAttribute(entity=entity, attribute=attribute))

            # Remove Attribute
            for attribute_name, attribute in attributes_state.items():
                if attribute_name not in entity.attributes:
                    migrations.append(RemoveAttribute(entity=entity, attribute=attribute))

            # Create/Update Group
            for group_name, group in entity.groups.items():
                # Update
                if group_name in groups_state:
                    group_state = groups_state[group_name]
                    # Add an Attribute to a Group
                    for attribute_name, attribute in group.attributes.items():
                        if attribute_name not in group_state.attributes:
                            migrations.append(
                                AddGroupAttribute(
                                    entity=entity, group=group, attribute=attribute
                                )
                            )
                    # Remove an Attribute from a Group
                    for attribute_name, attribute in group_state.attributes.items():
                        if attribute_name not in group.attributes:
                            migrations.append(
                                RemoveGroupAttribute(
                                    entity=entity, group=group, attribute=attribute
                                )
                            )
                # Create
                else:
                    migrations.append(CreateGroup(entity=entity, group=group))

            # Remove Group
            for group_name, group in groups_state.items():
                if group_name not in entity.groups:
                    migrations.append(RemoveGroup(entity=entity, group=group))

            if migrations:
                if entity.layout.type == LayoutType.HNHM:
                    migrations.extend(
                        [
                            RemoveEntityView(entity=entity),
                            RecreateEntityView(entity=entity),
                        ]
                    )
                plan.entities_migrations[entity.name] = PlanCollection(
                    type=PlanType.UPDATE,
                    migrations=migrations,
                )

        # Link: remove
        for link_name, link in self.data.links.items():
            if link_name not in core_links:
                plan.links_migrations[link_name] = PlanCollection(
                    type=PlanType.REMOVE,
                    migrations=[RemoveLink(link=link)],
                )

        # Entity: remove
        for entity_name, entity in self.data.entities.items():
            if entity_name not in core_entities:
                migrations = []

                if entity.layout.type == LayoutType.HNHM:
                    migrations.append(RemoveEntityView(entity=entity))

                    attributes_state = self.data.entities[entity_name].attributes
                    groups_state = self.data.entities[entity_name].groups
                    # Remove Attribute
                    for _, attribute_state in attributes_state.items():
                        migrations.append(
                            RemoveAttribute(entity=entity, attribute=attribute_state)
                        )
                    # Remove Group
                    for group_name, group in groups_state.items():
                        migrations.append(RemoveGroup(entity=entity, group=group))

                migrations.append(RemoveEntity(entity=entity))
                plan.entities_migrations[entity_name] = PlanCollection(
                    type=PlanType.REMOVE,
                    migrations=migrations,
                )

        # Link: create
        for link_name, link in core_links.items():
            if link_name not in self.data.links:
                plan.links_migrations[link.name] = PlanCollection(
                    type=PlanType.CREATE,
                    migrations=[CreateLink(link=link)],
                )

        return plan

    def apply(self, plan: Plan):
        for migration in plan.migrations_all:
            sql = self.sql.generate_sql(migration)

            match migration:
                case CreateEntity(entity=entity):
                    self.data.check_entity_not_exists(entity.name)
                    self.sql.execute(sql)
                    if entity.layout.type == LayoutType.HNHM:
                        attributes = {}
                        groups = {}
                    else:
                        attributes = entity.attributes
                        groups = entity.groups
                    self.data.entities[entity.name] = Entity(
                        name=entity.name,
                        layout=entity.layout,
                        doc=entity.doc,
                        keys=entity.keys,
                        attributes=attributes,
                        groups=groups,
                    )

                case RemoveEntity(entity=entity):
                    self.data.check_entity_exists(entity.name)
                    self.sql.execute(sql)
                    del self.data.entities[entity.name]

                case RecreateEntityView(entity=entity):
                    self.sql.execute(sql)
                    self.data.entities_views.add(entity.name)

                case RemoveEntityView(entity=entity):
                    if entity.name not in self.data.entities_views:
                        raise HnhmError(f"Entity's View '{entity.name}' doesn't exist.")
                    self.sql.execute(sql)
                    self.data.entities_views.remove(entity.name)

                case CreateAttribute(entity=entity, attribute=attribute):
                    self.data.check_attribute_not_exists(entity.name, attribute.name)
                    self.sql.execute(sql)
                    self.data.entities[entity.name].attributes[attribute.name] = attribute

                case RemoveAttribute(entity=entity, attribute=attribute):
                    self.data.check_attribute_exists(entity.name, attribute.name)
                    self.sql.execute(sql)
                    del self.data.entities[entity.name].attributes[attribute.name]

                case CreateGroup(entity=entity, group=group):
                    self.data.check_group_not_exists(entity.name, group.name)
                    self.sql.execute(sql)
                    self.data.entities[entity.name].groups[group.name] = group

                case RemoveGroup(entity=entity, group=group):
                    self.data.check_group_exists(entity.name, group.name)
                    self.sql.execute(sql)
                    del self.data.entities[entity.name].groups[group.name]

                case AddGroupAttribute(entity=entity, group=group, attribute=attribute):
                    self.data.check_group_attribute_not_exists(
                        entity.name, group.name, attribute.name
                    )
                    self.sql.execute(sql)
                    self.data.entities[entity.name].groups[group.name].attributes[
                        attribute.name
                    ] = attribute

                case RemoveGroupAttribute(
                    entity=entity, group=group, attribute=attribute
                ):
                    self.data.check_group_attribute_exists(
                        entity.name, group.name, attribute.name
                    )
                    self.sql.execute(sql)
                    del (
                        self.data.entities[entity.name]
                        .groups[group.name]
                        .attributes[attribute.name]
                    )

                case CreateLink(link=link):
                    self.data.check_link_not_exists(link.name)
                    self.sql.execute(sql)
                    self.data.links[link.name] = link

                case RemoveLink(link=link):
                    self.data.check_link_exists(link.name)
                    self.sql.execute(sql)
                    del self.data.links[link.name]

                case _:
                    raise HnhmError(f"Unknown migration: '{migration}'")
