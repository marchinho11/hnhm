from .hnhm_link import HnhmLink
from .hnhm_attribute import HnhmAttribute
from .hnhm_entity import HnhmEntity, LayoutType
from .core import Sql, Link, Entity, Attribute, HnhmError, task


class Flow:
    def __init__(self, *, source: HnhmEntity, business_time_field: HnhmAttribute):
        source = source.to_core()
        if source.layout.type != LayoutType.STAGE:
            raise HnhmError(
                f"Flow doesn't support loading from entities with layout type '{source.layout.type}'."
                " Please, use Flow to load data only from STAGE entities."
            )

        self.source = source
        self.business_time_field = business_time_field.to_core(source.name)

        # {entity_name -> {attribute_target -> attribute_source}}
        self._entities_keys_mappings: dict[str, dict[Attribute, Attribute]] = {}

        # {entity_name -> target}
        self._hubs: dict[str, Entity] = {}

        # {entity_name -> {attribute_target -> attribute_source}}
        self._attributes: dict[str, dict[Attribute, Attribute]] = {}

        # {entity_name -> {group_name -> {attribute_target -> attribute_source}}}
        self._groups: dict[str, dict[str, dict[Attribute, Attribute]]] = {}

        # {link_name -> {entity_name -> {attribute_target -> attribute_source}}}
        self._links: dict[str, Link] = {}

    @property
    def tasks(self) -> list[task.Task]:
        tasks = []
        hub_tasks = {}
        for target_name, target in self._hubs.items():
            keys_mapping = self._entities_keys_mappings[target_name]
            hub_tasks[target_name] = task.LoadHub(
                source=self.source,
                target=target,
                keys_mapping=keys_mapping,
                business_time_field=self.business_time_field,
            )

        for target_name, attributes_mapping in self._attributes.items():
            target = self._hubs[target_name]
            depends_on = [hub_tasks[target_name].id]
            keys_mapping = self._entities_keys_mappings[target_name]

            for target_attribute, source_attribute in attributes_mapping.items():
                tasks.append(
                    task.LoadAttribute(
                        source=self.source,
                        target=target,
                        keys_mapping=keys_mapping,
                        source_attribute=source_attribute,
                        target_attribute=target_attribute,
                        business_time_field=self.business_time_field,
                        depends_on=depends_on,
                    )
                )

        for target_name, groups_mapping in self._groups.items():
            target = self._hubs[target_name]
            depends_on = [hub_tasks[target_name].id]
            keys_mapping = self._entities_keys_mappings[target_name]
            for group_name, attributes_mapping in groups_mapping.items():
                group = target.groups[group_name]
                tasks.append(
                    task.LoadGroup(
                        source=self.source,
                        target=target,
                        group=group,
                        keys_mapping=keys_mapping,
                        attributes_mapping=attributes_mapping,
                        business_time_field=self.business_time_field,
                        depends_on=depends_on,
                    )
                )

        for link_name, link in self._links.items():
            keys_mapping_link = {}
            depends_on = []
            key_entities_names = []
            for link_element in link.elements:
                entity_name = link_element.entity.name
                depends_on.append(hub_tasks[entity_name].id)
                keys_mapping_link[entity_name] = self._entities_keys_mappings[entity_name]

                if link_element in link.keys:
                    key_entities_names.append(link_element.entity.name)

            tasks.append(
                task.LoadLink(
                    source=self.source,
                    link=link,
                    keys_mapping=keys_mapping_link,
                    key_entities_names=key_entities_names,
                    business_time_field=self.business_time_field,
                    depends_on=depends_on,
                )
            )

        tasks.extend(hub_tasks.values())
        tasks = sorted(tasks, key=lambda t: t.priority)
        return tasks

    def load(
        self,
        target: HnhmEntity | HnhmLink,
        mapping: dict[HnhmAttribute, HnhmAttribute] | None = None,
    ):
        match target:
            case HnhmEntity():
                target_entity = target.to_core()

                if not mapping:
                    raise HnhmError(
                        f"Mapping is required to load data for entity='{target_entity.name}'."
                        " Please, provide attributes mapping."
                    )

                if target_entity.layout.type != LayoutType.HNHM:
                    raise HnhmError(
                        "Loading is only supported to the entities with the LayoutType='HNHM'."
                        f" Your target entity='{target_entity.name}' has LayoutType='{target_entity.layout.type}'."
                    )

                keys_mapping = {}
                groups_mapping: dict[str, dict[Attribute, Attribute]] = {}
                attributes_mapping = {}
                for attribute_target, attribute_source in mapping.items():
                    attribute_target = attribute_target.to_core(target_entity.name)
                    attribute_source = attribute_source.to_core(self.source.name)
                    if attribute_target in target_entity.keys:
                        keys_mapping[attribute_target] = attribute_source
                    elif attribute_target.group:
                        group_name = attribute_target.group
                        if group_name not in groups_mapping:
                            groups_mapping[group_name] = {}
                        groups_mapping[group_name][attribute_target] = attribute_source
                    else:
                        attributes_mapping[attribute_target] = attribute_source

                # Check all attributes for a Group were mapped
                for group_name, group in target_entity.groups.items():
                    group_mapping = groups_mapping.get(group_name)
                    if not group_mapping:
                        continue

                    for attribute in group.attributes.values():
                        if attribute not in group_mapping:
                            attribute_full_name = (
                                f"{target_entity.name}.{group_name}.{attribute.name}"
                            )
                            raise HnhmError(
                                f"Mapping not found for the attribute '{attribute_full_name}'."
                                f" Please, provide all mappings for the group: '{target_entity.name}.{group_name}'."
                            )

                missing_keys = set(target_entity.keys) - set(keys_mapping.keys())
                if missing_keys:
                    missing_keys_names = [key.name for key in missing_keys]
                    raise HnhmError(
                        f"Found missing mappings for entity='{target_entity.name}' keys."
                        f" Missing mappings for keys: {missing_keys_names}."
                    )

                if target_entity.name in self._entities_keys_mappings:
                    raise HnhmError(
                        f"Found duplicated load for entity='{target_entity.name}'."
                        " Please, use single load() block for single entity."
                    )

                self._entities_keys_mappings[target_entity.name] = keys_mapping
                self._hubs[target_entity.name] = target_entity
                self._attributes[target_entity.name] = attributes_mapping
                self._groups[target_entity.name] = groups_mapping

            case HnhmLink():
                link = target.to_core()

                for element in link.elements:
                    if element.entity.name not in self._entities_keys_mappings:
                        raise HnhmError(
                            f"Keys mapping not found for entity='{element.entity.name}'."
                            " Please, provide mapping the entity keys."
                        )

                if link.name in self._links:
                    raise HnhmError(
                        f"Found duplicated load for link='{link.name}'."
                        " Please, use single load() block for single link."
                    )

                self._links[link.name] = link

            case _:
                target_type = type(target)
                raise HnhmError(f"Unknown target type '{target_type}'.")

        return self

    def execute(self, sql: Sql):
        for _task in self.tasks:
            sql.execute(sql.generate_sql(_task))
