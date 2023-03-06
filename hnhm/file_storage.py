import json
from pathlib import Path

from hnhm.core import Storage, HnhmStorageData


class FileStorage(Storage):
    def __init__(self, file_name: str):
        self.file_name = file_name

    def load(self) -> HnhmStorageData:
        if Path(self.file_name).is_file():
            return HnhmStorageData.parse_file(self.file_name)
        else:
            return HnhmStorageData(entities={}, links={})

    def save(self, data: HnhmStorageData):
        with open(self.file_name, "w") as f:
            json.dump(data.dict(), f, ensure_ascii=False, indent=2)
