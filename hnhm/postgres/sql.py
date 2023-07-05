import jinja2
import psycopg2

from ..core.attribute import Type
from ..core import Sql, HnhmError, ChangeType, LayoutType, task, migration

PG_TYPES = {
    Type.STRING: "TEXT",
    Type.INTEGER: "INTEGER",
    Type.FLOAT: "DOUBLE PRECISION",
    Type.TIMESTAMP: "TIMESTAMPTZ",
}


def generate_sql(
    migration_or_task: migration.Migration | task.Task, jinja: jinja2.Environment
) -> str:
    """Generates SQL for a given migration or task."""

    match migration_or_task:
        case migration.CreateEntity(entity=entity):
            columns_with_types = []
            if entity.layout.type == LayoutType.HNHM:
                template = jinja.get_template("create_hub.sql")
                for key in entity.keys:
                    column_name = key.name
                    column_type = PG_TYPES[key.type]
                    column_type = f"{column_type} NOT NULL"
                    columns_with_types.append((column_name, column_type))

            elif entity.layout.type == LayoutType.STAGE:
                template = jinja.get_template("create_stage.sql")
                for attribute in entity.attributes.values():
                    column_name = attribute.name
                    column_type = PG_TYPES[attribute.type]
                    columns_with_types.append((column_name, column_type))

            else:
                raise HnhmError(f"Unknown LayoutType='{entity.layout.type}'")

            return template.render(
                name=entity.name, columns_with_types=columns_with_types
            )

        case migration.RecreateEntityView(entity=entity):
            template = jinja.get_template("update_entity_view.sql")

            view_name = f"entity__{entity.name}"
            sk = entity.sk
            hub = f"hub__{entity.name}"

            selects = []
            for attribute in entity.attributes.values():
                selects.append((attribute.table, attribute.name, attribute.name))

            for group in entity.groups.values():
                for attribute in group.attributes.values():
                    selects.append(
                        (group.table, attribute.name, f"{group.name}__{attribute.name}")
                    )

            return template.render(
                view_name=view_name,
                sk=sk,
                hub=hub,
                selects=selects,
                attributes=entity.attributes.values(),
                groups=entity.groups.values(),
            )

        case migration.CreateAttribute(entity=entity, attribute=attribute):
            attribute_type = PG_TYPES[attribute.type]

            if entity.layout.type == LayoutType.STAGE:
                return f"ALTER TABLE stg__{entity.name} ADD COLUMN {attribute.name} {attribute_type}"

            is_scd2 = attribute.change_type == ChangeType.NEW

            template = jinja.get_template("create_attribute.sql")
            return template.render(
                entity_name=entity.name,
                attribute_name=attribute.name,
                attribute_type=attribute_type,
                is_scd2=is_scd2,
            )

        case migration.CreateGroup(entity=entity, group=group):
            columns = []
            for attribute in group.attributes.values():
                column_type = PG_TYPES[attribute.type]
                columns.append(f"{attribute.name} {column_type}")

            is_scd2 = group.change_type == ChangeType.NEW

            template = jinja.get_template("create_group.sql")
            return template.render(
                entity_name=entity.name,
                group_name=group.name,
                columns=columns,
                is_scd2=is_scd2,
            )

        case migration.AddGroupAttribute(entity=entity, group=group, attribute=attribute):
            attribute_type = PG_TYPES[attribute.type]
            return f"ALTER TABLE group__{entity.name}__{group.name} ADD COLUMN {attribute.name} {attribute_type}"

        case migration.CreateLink(link=link):
            entities = []
            for link_element in link.elements:
                entities.append(link_element.entity.name)

            primary_keys = ["valid_from"]
            for key in link.keys:
                primary_keys.append(f"{key.entity.name}_sk")

            template = jinja.get_template("create_link.sql")
            return template.render(
                name=link.name,
                entities=entities,
                primary_keys=primary_keys,
            )

        case migration.RemoveEntity(entity=entity):
            if entity.layout.type == LayoutType.HNHM:
                table_name = f"hub__{entity.name}"
            else:
                table_name = f"stg__{entity.name}"
            return f"DROP TABLE {table_name}"

        case migration.RemoveAttribute(entity=entity, attribute=attribute):
            if entity.layout.type == LayoutType.STAGE:
                return f"ALTER TABLE stg__{entity.name} DROP COLUMN {attribute.name}"

            return f"DROP TABLE attr__{entity.name}__{attribute.name}"

        case migration.RemoveGroup(entity=entity, group=group):
            return f"DROP TABLE group__{entity.name}__{group.name}"

        case migration.RemoveGroupAttribute(
            entity=entity, group=group, attribute=attribute
        ):
            return f"ALTER TABLE group__{entity.name}__{group.name} DROP COLUMN {attribute.name}"

        case migration.RemoveLink(link=link):
            return f"DROP TABLE link__{link.name}"

        case migration.RemoveEntityView(entity=entity):
            view_name = f"entity__{entity.name}"
            return f"DROP VIEW {view_name}"

        case task.LoadHub(
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

            template = jinja.get_template("load_hub.sql")
            return template.render(
                source_name=source.name,
                source_sk=source_sk,
                source_keys=source_keys,
                target_name=target.name,
                target_keys=target_keys,
                business_time_field=business_time_field.name,
            )

        case task.LoadAttribute(
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
                template = jinja.get_template("load_ignore.sql")
            elif target_attribute.change_type == ChangeType.UPDATE:
                template = jinja.get_template("load_update.sql")
            elif target_attribute.change_type == ChangeType.NEW:
                template = jinja.get_template("load_new.sql")
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
            )

        case task.LoadGroup(
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
                template = jinja.get_template("load_ignore.sql")
            elif group.change_type == ChangeType.UPDATE:
                template = jinja.get_template("load_update.sql")
            elif group.change_type == ChangeType.NEW:
                template = jinja.get_template("load_new.sql")
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
            )

        case task.LoadLink(
            source=source,
            link=link,
            business_time_field=business_time_field,
            keys_mapping=keys_mapping,
            key_entities_names=key_entities_names,
        ):
            source_table = f"stg__{source.name}"

            target_sks = []
            source_sks = []
            key_sks = []
            for entity_name, entity_keys_mapping in keys_mapping.items():
                source_keys = [
                    key_source.name for key_source in entity_keys_mapping.values()
                ]
                source_sk_components = (f"{key}::TEXT" for key in source_keys)
                source_sk_components = "|| '-' ||".join(source_sk_components)
                source_sk = f"MD5({source_sk_components})"
                source_sks.append(source_sk)

                target_sk = f"{entity_name}_sk"
                target_sks.append(target_sk)

                if entity_name in key_entities_names:
                    key_sks.append(target_sk)

            target_table = f"link__{link.name}"

            template = jinja.get_template("load_link.sql")
            return template.render(
                source_table=source_table,
                target_table=target_table,
                source_sks=source_sks,
                target_sks=target_sks,
                key_sks=key_sks,
                business_time_field=business_time_field.name,
            )

        case _:
            migration_or_task_type = type(migration_or_task)
            raise HnhmError(
                f"Unknown migration or task: '{migration_or_task}' with type='{migration_or_task_type}'."
            )


class PostgresPsycopgSql(Sql):
    def __init__(
        self,
        *,
        host: str = "localhost",
        port: int = 5432,
        database: str = "postgres",
        user: str = "postgres",
        password: str | None = None,
    ):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.jinja = jinja2.Environment(
            loader=jinja2.PackageLoader("hnhm.postgres", "sql_templates")
        )
        self.jinja.globals.update(zip=zip)

    def generate_sql(self, migration_or_task: migration.Migration | task.Task) -> str:
        return generate_sql(migration_or_task, self.jinja)

    def execute(self, sql: str):
        connection = psycopg2.connect(
            database=self.database,
            user=self.user,
            password=self.password,
            port=self.port,
            host=self.host,
        )
        cursor = connection.cursor()

        try:
            cursor.execute(sql)
            connection.commit()
        except Exception as e:
            raise e
        finally:
            cursor.close()
            connection.close()

    def execute_many(self, sql: str, values: list):
        connection = psycopg2.connect(
            database=self.database,
            user=self.user,
            password=self.password,
            port=self.port,
            host=self.host,
        )
        cursor = connection.cursor()

        try:
            cursor.executemany(sql, values)
            connection.commit()
        finally:
            cursor.close()
            connection.close()
