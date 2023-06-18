# hNhM
**hNhM**(highly Normalized hybrid Model) – data modeling methodology based on Anchor modeling and Data Vault. Implementation of this package is based on report **"How we implemented our data storage model — highly Normalized hybrid Model"** by Evgeny Ermakov and Nikolai Grebenshchikov. 
[1) Yandex Report, habr.com](https://habr.com/ru/company/yandex/blog/557140/). [2) SmartData Conference, youtube.com](https://youtu.be/2fPqDvHsd0w)

# Basic hNhM concepts
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
