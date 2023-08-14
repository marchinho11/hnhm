# <img src="https://raw.githubusercontent.com/marchinho11/hnhm/main/docs/assets/logo.png" height="40px">
[![codecov](https://codecov.io/gh/marchinho11/hnhm/branch/main/graph/badge.svg?token=PFB1111T2D)](https://codecov.io/gh/marchinho11/hnhm)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Downloads](https://static.pepy.tech/personalized-badge/hnhm?period=week&units=international_system&left_color=black&right_color=brightgreen&left_text=PyPi%20/%20week)](https://pepy.tech/project/hnhm)
[![Downloads](https://static.pepy.tech/personalized-badge/hnhm?period=total&units=international_system&left_color=black&right_color=brightgreen&left_text=PyPi%20/%20total)](https://pepy.tech/project/hnhm)
![Visitors](https://api.visitorbadge.io/api/combined?path=marchinho11%2Fhnhm&label=Visitors&labelColor=%23000000&countColor=%2347c21a&style=flat&labelStyle=none)

**hNhM**(highly Normalized hybrid Model) – data modeling methodology that enables iterative and Agile-driven
 modifications to your Data Warehouse (DWH). The methodology is based on Anchor Modeling and Data Vault.


The idea is to represent each Entity using 3 types of tables:
- `Hub` stores Business and Surrogate keys
- `Attribute` stores the history of changes (e.g. Name, Age, Gender...)
- `Group` is used to reduce the number of underlying tables by grouping multiple Attributes in one Group.
  **The best practice is to define a Group by the same data source.**


So, the purpose of `hnhm` is to:
* **Define** Entities, Links and Flows *declaratively* using Python
  * Describe them "logically"
  * The "physical" layer is managed by `hnhm`
* **Apply** the changes to a DWH iteratively
  * `hnhm` detects changes in the entities and creates new Attributes, Groups, or Links
* **Load** data from the Staging layer using Flows in the correct order
  * Ignore, Update, or keep the history using `SCD2`


Implementation of this package is based on report
 **"How we implemented our data storage model — highly Normalized hybrid Model"**
 by Evgeny Ermakov and Nikolai Grebenshchikov. [1) Yandex Report, habr.com](https://habr.com/ru/company/yandex/blog/557140/).
 [2) SmartData Conference, youtube.com](https://youtu.be/2fPqDvHsd0w)


* [Tutorial](#tutorial)
  + [Prerequisites](#prerequisites)
  + [Initialize DWH](#initialize-dwh)
  + [Start modeling](#start-modeling)
  + [Add Attribute and Group](#add-attribute-and-group)
* [Concepts](#concepts)
  + [Logical level (Python classes)](#logical-level-python-classes)
  + [Physical level (Tables)](#physical-level-tables)
  + [Change types of Attributes and Groups](#change-types-of-attributes-and-groups)
* [Supported Databases](#supported-databases)
* [Future plans](#future-plans)
* [Contribute!](#contribute)
* [Documentation](#documentation)


## Tutorial
You can find the full code in the [`dwh`](dwh) folder.

### Prerequisites
Install the library
```shell
pip install hnhm
```

Create the `dwh` directory
```shell
mkdir dwh
```

Spin up the Postgres Database
```shell
# dwh/docker-compose.yml
version: "3.9"

volumes:
  postgres_data: { }

services:
  postgres:
    image: postgres:15
    volumes:
      - "postgres_data:/var/lib/postgresql/data"
    ports:
      - "5433:5432"
    environment:
      POSTGRES_DB: hnhm
      POSTGRES_USER: hnhm
      POSTGRES_PASSWORD: 123
      
# $ docker compose up -d
```

### Initialize DWH
Create the `__hnhm__.py` file with the following contents:
```python
# dwh/__hnhm__.py
from hnhm import PostgresPsycopgSql, HnHm, HnhmRegistry, FileState

sql = PostgresPsycopgSql(
    database="hnhm",
    user="hnhm",
    password="123",
    port=5433
)

registry = HnhmRegistry(
    hnhm=HnHm(
        sql=sql,
        state=FileState("state.json"),
    ),
)
```

- `PostgresPsycopgSql` generates and executes SQL
- `HnhmRegistry` stores the `hnhm` object, entities and links
- `HnHm` implements core logic and manages the state
- `FileState` stores the state of your DWH in a file


Apply the changes to your DWH:
```shell
$ hnhm apply dwh

Importing 'registry' object from the module: 'dwh.__hnhm__'.

Your DWH is up to date.
```

Our DWH is up-to-date because we haven't added any entities and links yet.

### Start modeling
Let's add the new Entity. Add the `dwh/user.py` file with the following contents:
```python
# dwh/user.py
from hnhm import (
    Layout,
    LayoutType,
    String,
    ChangeType,
    HnhmEntity,
)


class User(HnhmEntity):
    """User data."""

    __layout__ = Layout(name="user", type=LayoutType.HNHM)

    user_id = String(comment="User ID.", change_type=ChangeType.IGNORE)

    __keys__ = [user_id]

```

Add the `User` entity to the registry:
```diff
# dwh/__hnhm__.py
from hnhm import PostgresPsycopgSql, HnHm, HnhmRegistry, FileState
+ from dwh.user import User

sql = PostgresPsycopgSql(
    database="hnhm",
    user="hnhm",
    password="123",
    port=5433
)

registry = HnhmRegistry(
+   entities=[User()],
    hnhm=HnHm(
        sql=sql,
        state=FileState("state.json"),
    ),
)
```

Apply the changes to your DWH:
```shell
$ hnhm apply dwh

Importing 'registry' object from the module: 'dwh.__hnhm__'.

Plan:

+ entity 'HNHM.user'
  + view 'user'
  + hub 'user'

Apply migrations? [y/N]: y
Applied!
```

We added the new entity `User` to our DWH
```sql
-- View on top the DDS tables
select * from entity__user;

-- Hub
select * from hub__user;
```

### Add Attribute and Group
Let's add an Attribute and a Group to our Entity. Edit the `dwh/user.py` file:
```diff
# dwh/user.py
from hnhm import (
    Layout,
    LayoutType,
    String,
    ChangeType,
    HnhmEntity,
+   Integer
)


class User(HnhmEntity):
    """User data."""

    __layout__ = Layout(name="user", type=LayoutType.HNHM)

    user_id = String(comment="User ID.", change_type=ChangeType.IGNORE)
+   age = Integer(comment="Age.", change_type=ChangeType.UPDATE)
+   first_name = String(comment="First name.", change_type=ChangeType.NEW, group="name")
+   last_name = String(comment="Last name.", change_type=ChangeType.NEW, group="name")

    __keys__ = [user_id]

```

Apply the changes to your DWH:
```shell
$ hnhm apply dwh

Importing 'registry' object from the module: 'dwh.__hnhm__'.

Plan:

[u] entity 'HNHM.user'
  + attribute 'age'
  + group 'name'
    |attribute 'first_name'
    |attribute 'last_name'
  [u] view 'user'

Apply migrations? [y/N]: y
Applied!
```


Take a look at newly created tables
```sql
-- View on top of the DDS tables was updated
select * from entity__user;

-- Attribute 'age'
select * from attr__user__age;

-- Group 'name'
select * from group__user__name;
```

The physical result:
```
view: entity__user
┌────────────────────────────────────────────────────────────────┐
│┌───────────────────┐   ┌────────────────┐   ┌─────────────────┐│
 │ group__user__name │   │ hub__user      │   │ attr__user__age │
 │                   │   │                │   │                 │
 │ + user_sk (FK)    ├──►│ + user_sk (PK) │◄──┤ + user_sk (FK)  │
 │ + first_name      │   │ + user_id_bk   │   │ + age           │
 │ + last_name       │   │ + valid_from   │   │ + valid_from    │
 │ + valid_from      │   │ + _hash        │   │ + _hash         │
 │ + valid_to        │   │ + _source      │   │ + _source       │
 │ + _hash           │   │ + _loaded_at   │   │ + _loaded_at    │
 │ + _source         │   └────────────────┘   └─────────────────┘
 │ + _loaded_at      │
 └───────────────────┘
```


## Concepts
### Logical level (Python classes)
* **Entity**: business entity (User, Review, Order, Booking)
* **Link**: the relationship between Entities (UserOrder, UserBooking)
* **Flow**: helps to load data from the stage layer to Entities and Links

### Physical level (Tables)
* **Hub**: hub table contains Entity's Business Keys and Surrogate Key(MD5 hash of concatenated business keys)
* **Attribute**: attribute table contains FK to Entity's surrogate key, history of attribute changes, and the `valid_from` column
* **Group**: group table contains FK to Entity's surrogate key, history of changes to group attributes, and the `valid_from` column
* **Link**: link table contains FKs to Entities surrogate keys. Historicity by `SCD2`

### Change types of Attributes and Groups
* `IGNORE`: insert the latest new data, ignore updates
* `UPDATE`: insert the latest new data, update
* `NEW`: full history using `SCD2`. Adds the `valid_to` column


## Supported Databases
- [x] Postgres
- [ ] GreenPlum
- [ ] Snowflake
- [ ] BigQuery
- [ ] ClickHouse


## Future plans
* New database connectors
  * Snowflake
  * BigQuery
  * GreenPlum
  * (?) ClickHouse
* Tests
  * More elegant DSL
* State management
  * Keep history in the database
  * Refresh: drift detection
  * Rollback
  * Generate static documentation for DWH
* Robustness
  * Reliability
  * Benchmarks
  * SQL optimization, refinement of Jinja code
* Documentation
  * Documentation for Python sources
  * Guides, best practices, and recipes
* Code Style & CI
  * Testing matrix
  * Adopt [`Ruff`](https://github.com/roman-right/beanie/blob/main/.pre-commit-config.yaml) or [`wemake-python-styleguide`](https://github.com/wemake-services/wemake-python-styleguide)


## Contribute!
What contributions are welcome? (**spoiler: any!**)
- New database connectors
- New features
- Typos correction
- Dependencies update
- Documentation improvement
- Code refinement
- Bug fixes


## Documentation
https://marchinho11.github.io/hnhm
