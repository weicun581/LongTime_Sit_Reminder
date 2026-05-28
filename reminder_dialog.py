from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QGuiApplication, QMouseEvent, QPixmap
from PyQt5.QtWidgets import QLabel, QWidget

from settings_panel import BACKGROUND_OPTIONS


BACKGROUND_IMAGE_PATHS = {key: path for key, _label, path in BACKGROUND_OPTIONS}


class ReminderDialog(QWidget):
    action_selected = pyqtSignal(str)
    Accepted = 1

    def __init__(self, background_key="image1", parent=None):
        super().__init__(parent)
        self.setWindowTitle("久坐提醒")
        self._action = None
        self._result = None
        self._background_key = background_key if background_key in BACKGROUND_IMAGE_PATHS else "image1"
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setAutoFillBackground(False)
        self.setWindowFlags(
            Qt.Window
            | Qt.Tool
            | Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
        )
        self.setStyleSheet(
            """
            QWidget {
                background: transparent;
            }
            QLabel#grassImageLabel {
                background: transparent;
            }
            QLabel#overlayLabel {
                background: rgba(34, 197, 94, 110);
            }
            """
        )

        self.image_label = QLabel(self)
        self.image_label.setObjectName("grassImageLabel")
        self.image_label.setAlignment(Qt.AlignCenter)

        self.overlay_label = QLabel(self)
        self.overlay_label.setObjectName("overlayLabel")
        self.overlay_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self.image_label.lower()
        self.overlay_label.raise_()

        self._original_pixmap = QPixmap(str(BACKGROUND_IMAGE_PATHS[self._background_key]))
        if not self._original_pixmap.isNull():
            self.image_label.setPixmap(self._original_pixmap)

        self._apply_primary_screen_geometry()
        self._refresh_scaled_pixmap()
        self.setWindowState(self.windowState() | Qt.WindowFullScreen)

    def _apply_primary_screen_geometry(self):
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return
        geometry = screen.geometry()
        self.setGeometry(geometry)
        self.move(geometry.topLeft())
        self.resize(geometry.size())
        self.image_label.setGeometry(self.rect())
        self.overlay_label.setGeometry(self.rect())

    def _refresh_scaled_pixmap(self):
        if self._original_pixmap.isNull():
            return
        self.image_label.setPixmap(
            self._original_pixmap.scaled(
                self.size(),
                Qt.IgnoreAspectRatio,
                Qt.SmoothTransformation,
            )
        )

    def showEvent(self, event):
        self._apply_primary_screen_geometry()
        self._refresh_scaled_pixmap()
        super().showEvent(event)
        self.showFullScreen()
        self._apply_primary_screen_geometry()
        self._refresh_scaled_pixmap()
        self.raise_()
        self.activateWindow()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_primary_screen_geometry()
        self._refresh_scaled_pixmap()

    def mousePressEvent(self, event: QMouseEvent):
        self._action = "complete"
        self._result = self.Accepted
        self.action_selected.emit(self._action)
        self.close()
        super().mousePressEvent(event)

    def get_action(self):
        return self._action

    def result(self):
        return self._result

    def has_grass_image(self):
        return not self._original_pixmap.isNull()

    def selected_background_key(self):
        return self._background_key

    def click_to_close_enabled(self):
        return True

    def runtime_overlay_snapshot(self):
        return {
            "geometry": self.geometry().getRect(),
            "frame_geometry": self.frameGeometry().getRect(),
            "is_visible": self.isVisible(),
            "is_full_screen": self.isFullScreen(),
            "stays_on_top": bool(self.windowFlags() & Qt.WindowStaysOnTopHint),
            "has_image": self.has_grass_image(),
            "click_to_close_enabled": self.click_to_close_enabled(),
            "has_translucent_style": "QLabel#overlayLabel" in self.styleSheet() and "rgba(34, 197, 94, 110)" in self.styleSheet(),
            "has_overlay_label": hasattr(self, "overlay_label") and self.overlay_label is not None,
            "background_key": self._background_key,
        }
