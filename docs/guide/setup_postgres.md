# Setup Postgres
Create a directory for the guide:
```shell
mkdir hnhm_guide
cd hnhm_guide
```

Let's set up Postgres database. You could use the following `docker-compose.yml` file to run Postgres:
```yaml
# docker-compose.yml 
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
```

Run Postgres with the following command:
```shell
docker-compose up -d

# [+] Running 3/3
#  ✔ Network hnhm_guide_default         Created                                                                                                                                      0.1s 
#  ✔ Volume "hnhm_guide_postgres_data"  Created                                                                                                                                      0.0s 
#  ✔ Container hnhm_guide-postgres-1    Started
```

Now you should have access to the `hnhm` database:
```shell
psql -h localhost -p 5433 -U hnhm hnhm
# Password for user hnhm: 123

~# \dt
# Did not find any relations.
```

File layout at the end of current step:
```
.
└── docker-compose.yml
```
