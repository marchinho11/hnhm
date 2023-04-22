from enum import Enum

import pydantic

from hnhm.core import (
    Sql,
    Entity,
    Storage,
    Mutation,
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

from .hnhm_link import HnhmLink
from .hnhm_entity import HnhmEntity


class PlanType(str, Enum):
    CREATE = "CREATE"
    REMOVE = "REMOVE"
    UPDATE = "UPDATE"


class PlanCollection(pydantic.BaseModel):
    type: PlanType
    mutations: list[Mutation]


class Plan(pydantic.BaseModel):
    entities_mutations: dict[str, PlanCollection]
    links_mutations: dict[str, PlanCollection]

    def is_empty(self):
        return not self.entities_mutations and not self.links_mutations

    @property
    def mutations_all(self):
        mutations: list[Mutation] = []
        for collection in self.entities_mutations.values():
            mutations.extend(collection.mutations)
        for collection in self.links_mutations.values():
            mutations.extend(collection.mutations)
        mutations = sorted(mutations, key=lambda m: m.priority)
        return mutations


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

        plan = Plan(entities_mutations={}, links_mutations={})

        # Entity: create if not exists
        for entity in core_entities.values():
            if entity.name in self.data.entities:
                continue

            # Create Entity
            mutations = [CreateEntity(entity=entity)]

            if entity.layout.type == LayoutType.HNHM:
                # Create Attribute
                for attribute in entity.attributes.values():
                    mutations.append(CreateAttribute(entity=entity, attribute=attribute))
                # Create Group
                for group in entity.groups.values():
                    mutations.append(CreateGroup(entity=entity, group=group))

            plan.entities_mutations[entity.name] = PlanCollection(
                type=PlanType.CREATE,
                mutations=mutations,
            )

        # Entity: create/remove/update Attribute/Group
        for entity in core_entities.values():
            if entity.name not in self.data.entities:
                continue

            attributes_state = self.data.entities[entity.name].attributes
            groups_state = self.data.entities[entity.name].groups

            mutations = []
            # Create Attribute
            for attribute_name, attribute in entity.attributes.items():
                if attribute_name not in attributes_state:
                    mutations.append(CreateAttribute(entity=entity, attribute=attribute))

            # Remove Attribute
            for attribute_name, attribute in attributes_state.items():
                if attribute_name not in entity.attributes:
                    mutations.append(RemoveAttribute(entity=entity, attribute=attribute))

            # Create/Update Group
            for group_name, group in entity.groups.items():
                # Update
                if group_name in groups_state:
                    group_state = groups_state[group_name]
                    # Add an Attribute to a Group
                    for attribute_name, attribute in group.attributes.items():
                        if attribute_name not in group_state.attributes:
                            mutations.append(
                                AddGroupAttribute(
                                    entity=entity, group=group, attribute=attribute
                                )
                            )
                    # Remove an Attribute from a Group
                    for attribute_name, attribute in group_state.attributes.items():
                        if attribute_name not in group.attributes:
                            mutations.append(
                                RemoveGroupAttribute(
                                    entity=entity, group=group, attribute=attribute
                                )
                            )
                # Create
                else:
                    mutations.append(CreateGroup(entity=entity, group=group))

            # Remove Group
            for group_name, group in groups_state.items():
                if group_name not in entity.groups:
                    mutations.append(RemoveGroup(entity=entity, group=group))

            if mutations:
                plan.entities_mutations[entity.name] = PlanCollection(
                    type=PlanType.UPDATE,
                    mutations=mutations,
                )

        # Link: remove
        for link_name, link in self.data.links.items():
            if link_name not in core_links:
                plan.links_mutations[link_name] = PlanCollection(
                    type=PlanType.REMOVE,
                    mutations=[RemoveLink(link=link)],
                )

        # Entity: remove
        for entity_name, entity in self.data.entities.items():
            if entity_name not in core_entities:
                mutations = []

                if entity.layout.type == LayoutType.HNHM:
                    attributes_state = self.data.entities[entity_name].attributes
                    groups_state = self.data.entities[entity_name].groups
                    # Remove Attribute
                    for _, attribute_state in attributes_state.items():
                        mutations.append(
                            RemoveAttribute(entity=entity, attribute=attribute_state)
                        )
                    # Remove Group
                    for group_name, group in groups_state.items():
                        mutations.append(RemoveGroup(entity=entity, group=group))

                mutations.append(RemoveEntity(entity=entity))
                plan.entities_mutations[entity_name] = PlanCollection(
                    type=PlanType.REMOVE,
                    mutations=mutations,
                )

        # Link: create
        for link_name, link in core_links.items():
            if link_name not in self.data.links:
                plan.links_mutations[link.name] = PlanCollection(
                    type=PlanType.CREATE,
                    mutations=[CreateLink(link=link)],
                )

        return plan

    def apply(self, plan: Plan):
        for mutation in plan.mutations_all:
            sql = self.sql.generate_sql(mutation)

            match mutation:
                case CreateEntity(entity=entity):
                    assert entity.name not in self.data.entities
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
                    assert entity.name in self.data.entities
                    self.sql.execute(sql)
                    del self.data.entities[entity.name]

                case CreateAttribute(entity=entity, attribute=attribute):
                    assert entity.name in self.data.entities
                    assert (
                        attribute.name not in self.data.entities[entity.name].attributes
                    )
                    self.sql.execute(sql)
                    self.data.entities[entity.name].attributes[attribute.name] = attribute

                case RemoveAttribute(entity=entity, attribute=attribute):
                    assert entity.name in self.data.entities
                    assert attribute.name in self.data.entities[entity.name].attributes
                    self.sql.execute(sql)
                    del self.data.entities[entity.name].attributes[attribute.name]

                case CreateGroup(entity=entity, group=group):
                    assert entity.name in self.data.entities
                    assert group.name not in self.data.entities[entity.name].groups
                    self.sql.execute(sql)
                    self.data.entities[entity.name].groups[group.name] = group

                case RemoveGroup(entity=entity, group=group):
                    assert entity.name in self.data.entities
                    assert group.name in self.data.entities[entity.name].groups
                    self.sql.execute(sql)
                    del self.data.entities[entity.name].groups[group.name]

                case AddGroupAttribute(entity=entity, group=group, attribute=attribute):
                    assert entity.name in self.data.entities
                    assert group.name in self.data.entities[entity.name].groups
                    assert (
                        attribute.name
                        not in self.data.entities[entity.name]
                        .groups[group.name]
                        .attributes
                    )
                    self.sql.execute(sql)
                    self.data.entities[entity.name].groups[group.name].attributes[
                        attribute.name
                    ] = attribute

                case RemoveGroupAttribute(
                    entity=entity, group=group, attribute=attribute
                ):
                    assert entity.name in self.data.entities
                    assert group.name in self.data.entities[entity.name].groups
                    assert (
                        attribute.name
                        in self.data.entities[entity.name].groups[group.name].attributes
                    )
                    self.sql.execute(sql)
                    del (
                        self.data.entities[entity.name]
                        .groups[group.name]
                        .attributes[attribute.name]
                    )

                case CreateLink(link=link):
                    assert link.name not in self.data.links
                    self.sql.execute(sql)
                    self.data.links[link.name] = link

                case RemoveLink(link=link):
                    assert link.name in self.data.links
                    self.sql.execute(sql)
                    del self.data.links[link.name]

                case _:
                    raise HnhmError(f"Unknown mutation: '{mutation}'")
