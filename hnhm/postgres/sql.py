from textwrap import dedent

import jinja2
from sqlalchemy import URL, Engine, text, create_engine

from hnhm.core import (
    Sql,
    Task,
    Type,
    LoadHub,
    LoadLink,
    Mutation,
    HnhmError,
    LoadGroup,
    ChangeType,
    CreateLink,
    LayoutType,
    RemoveLink,
    CreateGroup,
    RemoveGroup,
    CreateEntity,
    RemoveEntity,
    LoadAttribute,
    CreateAttribute,
    RemoveAttribute,
    AddGroupAttribute,
    RemoveGroupAttribute,
)

from .sql_templates import (
    SQL_TEMPLATE__LOAD_HUB,
    SQL_TEMPLATE__LOAD_NEW,
    SQL_TEMPLATE__CREATE_HUB,
    SQL_TEMPLATE__CREATE_LINK,
    SQL_TEMPLATE__LOAD_IGNORE,
    SQL_TEMPLATE__LOAD_UPDATE,
    SQL_TEMPLATE__CREATE_GROUP,
    SQL_TEMPLATE__CREATE_STAGE,
    SQL_TEMPLATE__CREATE_ATTRIBUTE,
)

PG_TYPES = {
    Type.STRING: "TEXT",
    Type.INTEGER: "INTEGER",
    Type.TIMESTAMP: "TIMESTAMPTZ",
}


def generate_sql(mutation_or_task: Mutation | Task, jinja: jinja2.Environment) -> str:
    match mutation_or_task:
        case CreateEntity(entity=entity):
            if entity.layout.type == LayoutType.HNHM:
                template = jinja.from_string(SQL_TEMPLATE__CREATE_HUB)
                columns = []
                columns_types = []
                for key in entity.keys:
                    columns.append(key.name)
                    column_type = PG_TYPES[key.type]
                    columns_types.append(f"{column_type} NOT NULL")

            elif entity.layout.type == LayoutType.STAGE:
                template = jinja.from_string(SQL_TEMPLATE__CREATE_STAGE)
                columns = []
                columns_types = []
                for attribute in entity.attributes.values():
                    columns.append(attribute.name)
                    columns_types.append(PG_TYPES[attribute.type])

            else:
                raise HnhmError(f"Unknown LayoutType='{entity.layout.type}'")

            return template.render(
                name=entity.name,
                columns=columns,
                columns_types=columns_types,
            )

        case CreateAttribute(entity=entity, attribute=attribute):
            attribute_type = PG_TYPES[attribute.type]

            if entity.layout.type == LayoutType.STAGE:
                return f"ALTER TABLE stg__{entity.name} ADD COLUMN {attribute.name} {attribute_type}"

            time_columns = ["valid_from TIMESTAMPTZ NOT NULL"]
            if attribute.change_type == ChangeType.NEW:
                time_columns.append("valid_to TIMESTAMPTZ")

            template = jinja.from_string(SQL_TEMPLATE__CREATE_ATTRIBUTE)
            return template.render(
                entity_name=entity.name,
                attribute_name=attribute.name,
                attribute_type=attribute_type,
                time_columns=time_columns,
            )

        case CreateGroup(entity=entity, group=group):
            columns = []
            for attribute in group.attributes.values():
                column_type = PG_TYPES[attribute.type]
                columns.append(f"{attribute.name} {column_type}")

            time_columns = ["valid_from TIMESTAMPTZ NOT NULL"]
            if group.change_type == ChangeType.NEW:
                time_columns.append("valid_to TIMESTAMPTZ")

            template = jinja.from_string(SQL_TEMPLATE__CREATE_GROUP)
            return template.render(
                entity_name=entity.name,
                group_name=group.name,
                columns=columns,
                time_columns=time_columns,
            )

        case AddGroupAttribute(entity=entity, group=group, attribute=attribute):
            attribute_type = PG_TYPES[attribute.type]
            return f"ALTER TABLE group__{entity.name}__{group.name} ADD COLUMN {attribute.name} {attribute_type}"

        case CreateLink(link=link):
            entities = []
            for link_element in link.elements:
                entities.append(link_element.entity.name)

            primary_keys = ["valid_from"]
            for key in link.keys:
                primary_keys.append(f"{key.entity.name}_sk")

            template = jinja.from_string(SQL_TEMPLATE__CREATE_LINK)
            return template.render(
                name=link.name,
                entities=entities,
                primary_keys=primary_keys,
            )

        case RemoveEntity(entity=entity):
            if entity.layout.type == LayoutType.HNHM:
                table_name = f"hub__{entity.name}"
            else:
                table_name = f"stg__{entity.name}"
            return f"DROP TABLE {table_name}"

        case RemoveAttribute(entity=entity, attribute=attribute):
            if entity.layout.type == LayoutType.STAGE:
                return f"ALTER TABLE stg__{entity.name} DROP COLUMN {attribute.name}"

            return f"DROP TABLE attr__{entity.name}__{attribute.name}"

        case RemoveGroup(entity=entity, group=group):
            return f"DROP TABLE group__{entity.name}__{group.name}"

        case RemoveGroupAttribute(entity=entity, group=group, attribute=attribute):
            return f"ALTER TABLE group__{entity.name}__{group.name} DROP COLUMN {attribute.name}"

        case RemoveLink(link=link):
            return f"DROP TABLE link__{link.name}"

        case LoadHub(
            source=source,
            target=target,
            business_time_field=business_time_field,
            keys_mapping=keys_mapping,
        ):
            source_keys = [key_source.name for key_source in keys_mapping.values()]
            source_sk_components = (f"{key}::TEXT" for key in source_keys)
            source_sk_components = "|| '-' ||".join(source_sk_components)
            source_sk = f"MD5({source_sk_components})"

            target_keys = [key.name for key in target.keys]

            template = jinja.from_string(SQL_TEMPLATE__LOAD_HUB)
            return template.render(
                source_name=source.name,
                source_sk=source_sk,
                source_keys=source_keys,
                target_name=target.name,
                target_keys=target_keys,
                business_time_field=business_time_field.name,
            )

        case LoadAttribute(
            source=source,
            target=target,
            business_time_field=business_time_field,
            keys_mapping=keys_mapping,
            source_attribute=source_attribute,
            target_attribute=target_attribute,
        ):
            source_table = f"stg__{source.name}"

            source_keys = [key_source.name for key_source in keys_mapping.values()]
            source_sk_components = (f"{key}::TEXT" for key in source_keys)
            source_sk_components = "|| '-' ||".join(source_sk_components)
            source_sk = f"MD5({source_sk_components})"

            source_attributes = [source_attribute.name]

            target_table = f"attr__{target.name}__{target_attribute.name}"
            target_sk = f"{target.name}_sk"
            target_sks = [f"{target.name}_sk"]

            target_attributes = [target_attribute.name]

            if target_attribute.change_type == ChangeType.IGNORE:
                template = jinja.from_string(SQL_TEMPLATE__LOAD_IGNORE)
            elif target_attribute.change_type == ChangeType.UPDATE:
                template = jinja.from_string(SQL_TEMPLATE__LOAD_UPDATE)
            elif target_attribute.change_type == ChangeType.NEW:
                template = jinja.from_string(SQL_TEMPLATE__LOAD_NEW)
            else:
                raise HnhmError(f"Unknown change type: '{target_attribute.change_type}'.")

            return template.render(
                source_table=source_table,
                source_sk=source_sk,
                source_sks=[source_sk],
                source_attributes=source_attributes,
                target_table=target_table,
                target_sk=target_sk,
                target_sks=target_sks,
                target_attributes=target_attributes,
                business_time_field=business_time_field.name,
                extra_sks=[],
            )

        case LoadGroup(
            source=source,
            target=target,
            group=group,
            business_time_field=business_time_field,
            keys_mapping=keys_mapping,
            attributes_mapping=attributes_mapping,
        ):
            source_table = f"stg__{source.name}"

            source_keys = [key_source.name for key_source in keys_mapping.values()]
            source_sk_components = (f"{key}::TEXT" for key in source_keys)
            source_sk_components = "|| '-' ||".join(source_sk_components)
            source_sk = f"MD5({source_sk_components})"

            source_attributes = [
                source_attribute.name for source_attribute in attributes_mapping.values()
            ]

            target_table = f"group__{target.name}__{group.name}"
            target_sk = f"{target.name}_sk"
            target_sks = [target_sk]

            target_attributes = [
                target_attribute.name for target_attribute in attributes_mapping
            ]

            if group.change_type == ChangeType.IGNORE:
                template = jinja.from_string(SQL_TEMPLATE__LOAD_IGNORE)
            elif group.change_type == ChangeType.UPDATE:
                template = jinja.from_string(SQL_TEMPLATE__LOAD_UPDATE)
            elif group.change_type == ChangeType.NEW:
                template = jinja.from_string(SQL_TEMPLATE__LOAD_NEW)
            else:
                raise HnhmError(f"Unknown change type: '{group.change_type}'.")

            return template.render(
                source_table=source_table,
                source_sk=source_sk,
                source_sks=[source_sk],
                source_attributes=source_attributes,
                target_table=target_table,
                target_sk=target_sk,
                target_sks=target_sks,
                target_attributes=target_attributes,
                business_time_field=business_time_field.name,
                extra_sks=[],
            )

        case LoadLink(
            source=source,
            link=link,
            business_time_field=business_time_field,
            keys_mapping=keys_mapping,
        ):
            source_table = f"stg__{source.name}"

            target_sks = []
            source_sks = []
            for entity_name, entity_keys_mapping in keys_mapping.items():
                source_keys = [
                    key_source.name for key_source in entity_keys_mapping.values()
                ]
                source_sk_components = (f"{key}::TEXT" for key in source_keys)
                source_sk_components = "|| '-' ||".join(source_sk_components)
                source_sk = f"MD5({source_sk_components})"

                target_sks.append(f"{entity_name}_sk")
                source_sks.append(source_sk)

            target_table = f"link__{link.name}"

            template = jinja.from_string(SQL_TEMPLATE__LOAD_NEW)
            return template.render(
                source_table=source_table,
                source_sks=source_sks,
                source_attributes=[],
                target_table=target_table,
                target_sks=target_sks,
                target_attributes=[],
                business_time_field=business_time_field.name,
                extra_sks=["valid_from"],
            )

        case _:
            mutation_or_task_type = type(mutation_or_task)
            raise HnhmError(
                f"Unknown mutation or task: '{mutation_or_task}' with type='{mutation_or_task_type}'."
            )


class PostgresSqlalchemySql(Sql):
    def __init__(
        self,
        *,
        host: str = "localhost",
        port: int = 5432,
        database: str = "postgres",
        user: str = "postgres",
        password: str | None = None,
        engine: Engine | None = None,
    ):
        if engine:
            self.engine = engine
        else:
            connection_url = URL.create(
                "postgresql+psycopg2",
                username=user,
                password=password,
                host=host,
                database=database,
                port=port,
            )
            self.engine = create_engine(connection_url)

        self.jinja = jinja2.Environment()
        self.jinja.globals.update(zip=zip)

    @classmethod
    def with_engine(cls, engine: Engine):
        if engine.url.drivername != "postgresql+psycopg2":
            raise HnhmError(
                f"Wrong driver name '{engine.url.drivername}'. Required: 'postgresql+psycopg2'."
            )
        return cls(engine=engine)

    def generate_sql(self, mutation_or_task: Mutation | Task) -> str:
        return generate_sql(mutation_or_task, self.jinja)

    def execute(self, sql: str, debug: bool = False):
        if debug:
            print(dedent(sql).strip())

        conn = None
        try:
            conn = self.engine.connect()
            conn.execute(text(sql))
            conn.commit()
        except Exception as e:
            raise e
        finally:
            if conn:
                conn.close()
            self.engine.dispose()
