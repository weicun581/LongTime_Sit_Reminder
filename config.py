import configparser
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AppConfig:
    interval_seconds: int = 3600
    background_key: str = "image1"

    @classmethod
    def load(cls, config_path):
        path = Path(config_path)
        if not path.exists():
            return cls()

        if path.suffix.lower() == ".ini":
            parser = configparser.ConfigParser()
            parser.read(path, encoding="utf-8")
            return cls(
                interval_seconds=parser.getint("timer", "interval_seconds", fallback=3600),
                background_key=parser.get("reminder", "background", fallback="image1"),
            )

        data = json.loads(path.read_text(encoding="utf-8"))
        if "interval_seconds" in data:
            interval_seconds = int(data["interval_seconds"])
        else:
            interval_seconds = int(data.get("interval_minutes", 60)) * 60
        return cls(interval_seconds=interval_seconds, background_key=data.get("background_key", "image1"))

    def save(self, config_path):
        path = Path(config_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix.lower() == ".ini":
            parser = configparser.ConfigParser()
            parser["timer"] = {"interval_seconds": str(self.interval_seconds)}
            parser["reminder"] = {"background": self.background_key}
            with path.open("w", encoding="utf-8") as config_file:
                parser.write(config_file)
            return
        path.write_text(
            json.dumps(
                {
                    "interval_seconds": self.interval_seconds,
                    "background_key": self.background_key,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
