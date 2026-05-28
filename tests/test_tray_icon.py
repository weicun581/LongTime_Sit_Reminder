import pathlib
import sys
import unittest

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tray_icon import TrayIcon


class TrayIconLifecycleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_tray_icon_keeps_parent_widget_reference(self):
        parent = QWidget()
        tray_icon = TrayIcon(QIcon(), parent=parent)

        self.assertIs(tray_icon.parent(), parent)
        self.assertIsNotNone(tray_icon.contextMenu())


if __name__ == "__main__":
    unittest.main()
