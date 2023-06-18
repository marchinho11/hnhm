# Setup Python
## Create virtualelnv
1. Install Python with version `>= 3.10`.
2. Create virtualenv (personally, I prefer [poetry](https://python-poetry.org/)):
   ```shell
   python -m virtualenv venv
   source ./venv/bin/activate
   ```

## Install required packages
Create the file `requirements.txt`:
```text
# requirements.txt
psycopg2-binary==2.9.6
hnhm
```

Install packages:
```shell
pip install -r requirements.txt
```

File layout at the end of current step:
```
.
├── docker-compose.yml
├── requirements.txt
└── venv
```
