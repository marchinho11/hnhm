from pathlib import Path

from .core import State, HnhmStateData


class FileState(State):
    def __init__(self, file_name: str):
        self.file_name = file_name

    def load(self) -> HnhmStateData:
        if Path(self.file_name).is_file():
            with open(self.file_name) as file_state:
                return HnhmStateData.model_validate_json(file_state.read())
        else:
            return HnhmStateData(entities={}, entities_views=set(), links={})

    def save(self, data: HnhmStateData):
        with open(self.file_name, "w") as f:
            f.write(data.model_dump_json(indent=2))
