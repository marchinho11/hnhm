# <img src="docs/assets/logo.png" height="40px">
[![codecov](https://codecov.io/gh/marchinho11/hnhm/branch/main/graph/badge.svg?token=PFB1111T2D)](https://codecov.io/gh/marchinho11/hnhm)
[![Release](https://github.com/marchinho11/hnhm/actions/workflows/release.yaml/badge.svg?branch=main&event=push)](https://github.com/marchinho11/hnhm/actions/workflows/release.yaml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Downloads](https://static.pepy.tech/personalized-badge/hnhm?period=week&units=international_system&left_color=black&right_color=brightgreen&left_text=PyPi%20/%20week)](https://pepy.tech/project/hnhm)
[![Downloads](https://static.pepy.tech/personalized-badge/hnhm?period=total&units=international_system&left_color=black&right_color=brightgreen&left_text=PyPi%20/%20total)](https://pepy.tech/project/hnhm)
![Visitors](https://api.visitorbadge.io/api/combined?path=marchinho11%2Fhnhm&label=Visitors&labelColor=%23000000&countColor=%2347c21a&style=flat&labelStyle=none)

**hNhM**(highly Normalized hybrid Model) – data modeling methodology based on Anchor modeling and Data Vault. Implementation of this package is based on report **"How we implemented our data storage model — highly Normalized hybrid Model"** by Evgeny Ermakov and Nikolai Grebenshchikov. 
[1) Yandex Report, habr.com](https://habr.com/ru/company/yandex/blog/557140/). [2) SmartData Conference, youtube.com](https://youtu.be/2fPqDvHsd0w)
* [Documentation](#documentation)
* [Basic hNhM concepts](#basic-hnhm-concepts)
* [Quick Start](#quick-start)

### Documentation
https://marchinho11.github.io/hnhm

### Basic hNhM concepts
**Logical level**
* **Entity**: business entity (User, Review, Order, Booking)
* **Link**: relationship between Entities (UserOrder, UserBooking)
* **Flow**: helps to load data from the stage layer to Entities and Links

**Physical level - tables**
* **Hub**: hub table contains Entity's Business Keys and Surrogate Key(MD5 hash of concatenated business keys)
* **Attribute**: attribute table contains FK to Entity's surrogate key, history of attribute changes, and the `valid_from` column
* **Group**: group table contains FK to Entity's surrogate key, history of changes to group attributes, and the `valid_from` column
* **Link**: link table contains FKs to Entities surrogate keys. Historicity by `SCD2`

**Change types of Attributes and Groups**
* `IGNORE`: insert the latest new data, ignore updates
* `UPDATE`: insert the latest new data, update
* `NEW`: full history using `SCD2`. Adds the `valid_to` column

## Quick Start
Install `hnhm` library
```shell
pip install hnhm
```

Create a directory with the name `dwh` and put the `__hnhm__.py` file there with the following contents:

```python
# dwh/__hnhm__.py
from hnhm import (
    Layout,
    LayoutType,
    String,
    Integer,
    ChangeType,
    HnHm,
    HnhmEntity,
    HnhmRegistry,
    FileState,
    PostgresPsycopgSql
)


class User(HnhmEntity):
    """User data."""

    __layout__ = Layout(name="user", type=LayoutType.HNHM)

    user_id = String(comment="User ID.", change_type=ChangeType.IGNORE)
    age = Integer(comment="Age.", change_type=ChangeType.UPDATE)
    first_name = String(comment="First name.", change_type=ChangeType.NEW, group="name")
    last_name = String(comment="Last name.", change_type=ChangeType.NEW, group="name")

    __keys__ = [user_id]

sql=PostgresPsycopgSql(database="hnhm", user="postgres")

registry = HnhmRegistry(
    entities=[User()],
    hnhm=HnHm(
        state=FileState("state.json"),
        sql=sql,
    ),
)
```

Apply the changes to your DWH:
```shell
$ hnhm apply dwh

Plan:

+ entity 'HNHM.user'
  + view 'user'
  + hub 'user'
  + attribute 'age'
  + group 'name'
    |attribute 'first_name'
    |attribute 'last_name'

Apply migrations? [y/N]: y
Applied!
```

The physical result of applied changes:
```
view: entity__user
┌────────────────────────────────────────────────────────────────┐
│┌───────────────────┐   ┌────────────────┐   ┌─────────────────┐│
 │ group__user__name │   │ hub__user      │   │ attr__user__age │
 │                   │   │                │   │                 │
 │ + user_sk (FK)    ├──►│ + user_sk (PK) │◄──┤ + user_sk (FK)  │
 │ + first_name      │   │ + user_id_bk   │   │ + age           │
 │ + last_name       │   │ + valid_from   │   │ + valid_from    │
 │ + valid_from      │   │ + _source      │   │ + _source       │
 │ + valid_to        │   │ + _loaded_at   │   │ + _loaded_at    │
 │ + _source         │   └────────────────┘   └─────────────────┘
 │ + _loaded_at      │
 └───────────────────┘
```
