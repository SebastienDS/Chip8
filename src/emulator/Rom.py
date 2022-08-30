from pathlib import Path
from typing import List


class Rom:
    def __init__(self, path: Path):
        assert path.is_file(), "Rom path must be a valid file"
        self.path = path

    def __str__(self) -> str:
        return " ".join((hex(value) for value in self.load_data()))

    def load_data(self) -> List[int]:
        with self.path.open("rb") as rom:
            content = rom.read()
            data = [int(value) for value in content]

        return data