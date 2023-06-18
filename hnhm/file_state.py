from pathlib import Path

from .core import State, HnhmStateData


class FileState(State):
    def __init__(self, file_name: str):
        self.file_name = file_name

    def load(self) -> HnhmStateData:
        if Path(self.file_name).is_file():
            return HnhmStateData.parse_file(self.file_name)
        else:
            return HnhmStateData(entities={}, entities_views=set(), links={})

    def save(self, data: HnhmStateData):
        with open(self.file_name, "w") as f:
            f.write(data.json(ensure_ascii=False, indent=2))
