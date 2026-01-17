import json
from pathlib import Path


class SaveSystem:
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self._data = self._load_data()

    def _load_data(self):
        if self.file_path.exists():
            try:
                with self.file_path.open("r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                raise FileNotFoundError("Save file is corrupted")
        return {}

    def _save_data(self):
        with self.file_path.open("w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=4)

    def load(self, id: str, default=None) -> dict[str, any]:
        return self._data.get(id, default)

    def save(self, id: str, value: dict[str, any]) -> None:
        self._data[id] = value
        self._save_data()