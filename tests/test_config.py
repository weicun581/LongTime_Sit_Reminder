import pathlib
import sys
import tempfile
import unittest

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import AppConfig


class AppConfigTest(unittest.TestCase):
    def test_load_returns_default_interval_seconds_when_file_missing(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = pathlib.Path(tmp_dir) / "config.json"

            config = AppConfig.load(config_path)

            self.assertEqual(config.interval_seconds, 3600)

    def test_save_and_reload_preserves_interval_seconds(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = pathlib.Path(tmp_dir) / "config.json"
            config = AppConfig(interval_seconds=45)

            config.save(config_path)
            loaded = AppConfig.load(config_path)

            self.assertEqual(loaded.interval_seconds, 45)


if __name__ == "__main__":
    unittest.main()
