# <img src="assets/logo.png" height="40px">
[![codecov](https://codecov.io/gh/marchinho11/hnhm/branch/main/graph/badge.svg?token=PFB1111T2D)](https://codecov.io/gh/marchinho11/hnhm)
[![Release](https://github.com/marchinho11/hnhm/actions/workflows/release.yaml/badge.svg?branch=main&event=push)](https://github.com/marchinho11/hnhm/actions/workflows/release.yaml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**hNhM**(highly Normalized hybrid Model) – data modeling methodology based on Anchor modeling and Data Vault. Implementation of this package is based on report **"How we implemented our data storage model — highly Normalized hybrid Model"** by Evgeny Ermakov and Nikolai Grebenshchikov. 
[1) Yandex Report, habr.com](https://habr.com/ru/company/yandex/blog/557140/). [2) SmartData Conference, youtube.com](https://youtu.be/2fPqDvHsd0w)

* [Basic hNhM concepts](#basic-hnhm-concepts)
* [Quick Start](#quick-start)
* [DWH example](#dwh-example)
* [Guide](#guide)

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

Create a directory with the name `dwh` and put the `__init__.py` file there with the following contents:
```python
# dwh/__init__.py
from hnhm import (
    Layout,
    LayoutType,
    String,
    Integer,
    ChangeType,
    HnHm,
    HnhmEntity,
    HnhmRegistry,
    FileStorage,
    PostgresSqlalchemySql
)


class User(HnhmEntity):
    """User data."""

    __layout__ = Layout(name="user", type=LayoutType.HNHM)

    user_id = String(comment="User ID.", change_type=ChangeType.IGNORE)
    age = Integer(comment="Age.", change_type=ChangeType.UPDATE)
    first_name = String(comment="First name.", change_type=ChangeType.NEW, group="name")
    last_name = String(comment="Last name.", change_type=ChangeType.NEW, group="name")

    __keys__ = [user_id]

    
__registry__ = HnhmRegistry(
    entities=[User()],
    hnhm=HnHm(
        storage=FileStorage("state.json"),
        sql=PostgresSqlalchemySql(database="hnhm", user="postgres"),
    ),
)
```

Apply the changes to your DWH:
```shell
$ hnhm apply dwh

Plan:

+ entity 'user'
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

## DWH example
Full DWH example including Entities, Links and Flows can be found in the [`dwh/`](dwh/) directory.

## Guide
