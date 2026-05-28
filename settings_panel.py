from pathlib import Path

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from settings_dialog import SettingsDialog


BACKGROUND_OPTIONS = [
    ("image1", "图片1", Path(__file__).resolve().parent / "docs" / "assets" / "grass_reminder.png"),
    ("image2", "图片2", Path(__file__).resolve().parent / "docs" / "assets" / "grass_reminder.png"),
    ("image3", "图片3", Path(__file__).resolve().parent / "docs" / "assets" / "grass_reminder.png"),
]


class SettingsPanel(QWidget):
    interval_changed = pyqtSignal(int)
    background_changed = pyqtSignal(str)

    def __init__(self, interval_seconds, background_key, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.timer_button = QPushButton("计时器", self)
        self.background_button = QPushButton("更换提醒背景", self)
        self.timer_button.clicked.connect(self.show_timer_page)
        self.background_button.clicked.connect(self.show_background_page)

        self.stacked_widget = QStackedWidget(self)
        self.timer_page = SettingsDialog(interval_seconds=interval_seconds, parent=self)
        self.timer_page.button_box.accepted.disconnect()
        self.timer_page.button_box.rejected.disconnect()
        self.timer_page.ok_button.clicked.connect(self._save_interval)
        self.timer_page.cancel_button.clicked.connect(self.close)
        self.stacked_widget.addWidget(self.timer_page)

        self.background_page = QWidget(self)
        self.background_layout = QVBoxLayout(self.background_page)
        self.background_group = QButtonGroup(self)
        self.background_group.setExclusive(False)
        self.background_checkboxes = {}
        for key, label, _path in BACKGROUND_OPTIONS:
            checkbox = QCheckBox(label, self.background_page)
            checkbox.toggled.connect(lambda checked, selected_key=key: self._handle_background_toggled(selected_key, checked))
            self.background_layout.addWidget(checkbox)
            self.background_group.addButton(checkbox)
            self.background_checkboxes[key] = checkbox
        self.background_layout.addStretch(1)
        self.stacked_widget.addWidget(self.background_page)

        nav_layout = QVBoxLayout()
        nav_layout.addWidget(self.timer_button)
        nav_layout.addWidget(self.background_button)
        nav_layout.addStretch(1)

        layout = QHBoxLayout(self)
        layout.addLayout(nav_layout)
        layout.addWidget(self.stacked_widget, 1)

        self.select_background(background_key)
        self.show_timer_page()

    def show_timer_page(self):
        self.stacked_widget.setCurrentWidget(self.timer_page)

    def show_background_page(self):
        self.stacked_widget.setCurrentWidget(self.background_page)

    def select_background(self, background_key):
        target_key = background_key if background_key in self.background_checkboxes else "image1"
        for key, checkbox in self.background_checkboxes.items():
            checkbox.blockSignals(True)
            checkbox.setChecked(key == target_key)
            checkbox.blockSignals(False)
        self._selected_background_key = target_key

    def selected_background_key(self):
        return self._selected_background_key

    def _handle_background_toggled(self, selected_key, checked):
        if not checked:
            if selected_key == self._selected_background_key:
                self.background_checkboxes[selected_key].blockSignals(True)
                self.background_checkboxes[selected_key].setChecked(True)
                self.background_checkboxes[selected_key].blockSignals(False)
            return
        self.select_background(selected_key)
        self.background_changed.emit(selected_key)

    def _save_interval(self):
        if not self.timer_page.try_accept():
            return
        self.interval_changed.emit(self.timer_page.get_interval_seconds())
        self.close()
