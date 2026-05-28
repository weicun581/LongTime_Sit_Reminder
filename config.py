import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AppConfig:
    interval_seconds: int = 3600

    @classmethod
    def load(cls, config_path):
        path = Path(config_path)
        if not path.exists():
            return cls()

        data = json.loads(path.read_text(encoding="utf-8"))
        if "interval_seconds" in data:
            interval_seconds = int(data["interval_seconds"])
        else:
            interval_seconds = int(data.get("interval_minutes", 60)) * 60
        return cls(interval_seconds=interval_seconds)

    def save(self, config_path):
        path = Path(config_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"interval_seconds": self.interval_seconds}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
