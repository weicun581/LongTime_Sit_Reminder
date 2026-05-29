import ctypes
import sys
import time
from pathlib import Path


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

from PyQt5.QtCore import QObject, QTimer, Qt
from PyQt5.QtGui import QCloseEvent, QIcon, QKeySequence
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QGridLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QShortcut,
    QStyle,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

APP_VERSION = "0.3.0"

from config import AppConfig
from history_dialog import HistoryDialog, RunHistoryDialog
from reminder_dialog import ReminderDialog
from reminder_scheduler import ReminderScheduler
from run_history import RunHistoryStore
from settings_dialog import SettingsDialog
from settings_panel import SettingsPanel
from tray_icon import TrayIcon


class AppController(QObject):
    def __init__(self, app, base_dir):
        super().__init__()
        self.app = app
        self.base_dir = Path(base_dir)
        self.config_path = self.base_dir / "config.ini"
        self.config = AppConfig.load(self.config_path)
        self.scheduler = ReminderScheduler(
            interval_seconds=self.config.interval_seconds,
            snooze_seconds=5 * 60,
        )
        self.reminder_dialog = None
        self.history_dialog = None
        self.run_history_dialog = None
        self.settings_panel = None
        self.history_markdown_path = self.base_dir / "res" / "version_history.md"
        self.run_history_path = self.base_dir / "run_history.json"
        self.run_history_store = RunHistoryStore(None if Path(base_dir) == Path(__file__).resolve().parent else self.run_history_path)
        self._active_run_started_at = None

        self.check_timer = QTimer(self)
        self.check_timer.setInterval(1000)
        self.check_timer.timeout.connect(self._check_due)

        self.preview_window = self._create_preview_window()
        self.preview_window.closeEvent = self._handle_preview_close

        self.tray_icon = TrayIcon(self._build_icon(), parent=None)
        self.tray_icon.setToolTip("Long Sit Reminder")
        self.tray_icon.show_main_page_action.triggered.connect(self.show_main_page)
        self.tray_icon.settings_action.triggered.connect(self.show_settings_panel)
        self.tray_icon.history_action.triggered.connect(self.show_history_dialog)
        self.tray_icon.exit_action.triggered.connect(self.quit_app)
        self.tray_icon.set_double_click_handler(self.show_main_page)

    def show_main_page(self):
        self.preview_window.show()
        self.preview_window.raise_()
        self.preview_window.activateWindow()

        now_ts = self._now_ts()
        self._update_countdown_display(now_ts=now_ts)

    def _create_preview_window(self):
        window = QMainWindow()
        window.setWindowTitle(f"久坐提醒 v{APP_VERSION}")
        window.setWindowIcon(self._build_icon())
        window.setMinimumWidth(420)
        window.setObjectName("previewWindow")

        central_widget = QWidget(window)
        central_widget.setObjectName("previewCentralWidget")
        central_widget.setStyleSheet(
            """
            QWidget#previewCentralWidget {
                background: #f3f6fb;
            }
            QLabel {
                color: #4b5563;
            }
            #previewStatusLabel {
                font-size: 16px;
                font-weight: 600;
                color: #2563eb;
            }
            #previewCountdownLabel {
                font-size: 44px;
                font-weight: 700;
                color: #111827;
            }
            QPushButton {
                min-height: 40px;
                border-radius: 10px;
                padding: 0 16px;
                font-size: 14px;
                font-weight: 600;
            }
            #primaryActionButton {
                background: #2563eb;
                color: white;
                border: none;
            }
            #primaryActionButton:hover {
                background: #1d4ed8;
            }
            #secondaryActionButton {
                background: white;
                color: #374151;
                border: 1px solid #cbd5e1;
            }
            #secondaryActionButton:hover {
                background: #f8fafc;
            }
            """
        )
        window.setCentralWidget(central_widget)

        self.preview_settings_action = QAction("设置", window)
        self.preview_settings_action.triggered.connect(self.show_settings_panel)
        self.preview_history_action = QAction("历史版本", window)
        self.preview_history_action.triggered.connect(self.show_history_dialog)
        self.preview_run_history_action = QAction("运行记录", window)
        self.preview_run_history_action.triggered.connect(self.show_run_history_dialog)
        window.menuBar().addAction(self.preview_settings_action)
        window.menuBar().addAction(self.preview_history_action)
        window.menuBar().addAction(self.preview_run_history_action)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        self.preview_status_label = QLabel("距离下次提醒", central_widget)
        self.preview_status_label.setObjectName("previewStatusLabel")
        self.preview_status_label.setAlignment(Qt.AlignCenter)
        self.preview_countdown_label = QLabel("60:00", central_widget)
        self.preview_countdown_label.setObjectName("previewCountdownLabel")
        self.preview_countdown_label.setAlignment(Qt.AlignCenter)
        layout.addSpacing(8)
        layout.addWidget(self.preview_status_label)
        layout.addWidget(self.preview_countdown_label)
        layout.addSpacing(8)

        self.preview_toggle_button = QPushButton("开始", central_widget)
        self.preview_toggle_button.setObjectName("primaryActionButton")
        self.preview_reset_button = QPushButton("重置", central_widget)
        self.preview_reset_button.setObjectName("secondaryActionButton")
        self.preview_toggle_button.clicked.connect(self.toggle_countdown)
        self.preview_reset_button.clicked.connect(self.reset_countdown)

        self.preview_toggle_shortcut = QShortcut(QKeySequence(Qt.Key_Space), window)
        self.preview_toggle_shortcut.activated.connect(self.toggle_countdown)

        self.preview_reminder_button = QPushButton("预览提醒弹窗", central_widget)
        self.preview_reminder_button.setObjectName("secondaryActionButton")
        self.preview_reminder_button.clicked.connect(self.show_reminder_preview)

        self.preview_button_layout = QGridLayout()
        self.preview_button_layout.setHorizontalSpacing(12)
        self.preview_button_layout.setVerticalSpacing(12)
        self.preview_button_layout.addWidget(self.preview_toggle_button, 0, 0)
        self.preview_button_layout.addWidget(self.preview_reset_button, 0, 1)
        self.preview_button_layout.addWidget(self.preview_reminder_button, 1, 0)
        layout.addLayout(self.preview_button_layout)

        return window

    def start(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "错误", "当前系统不支持系统托盘")
            return False

        self.app.setQuitOnLastWindowClosed(False)
        self.tray_icon.show()
        self.preview_window.show()
        self.preview_window.raise_()
        self.preview_window.activateWindow()
        self.scheduler.start(now_ts=self._now_ts())
        self._update_countdown_display(now_ts=self._now_ts())
        self.check_timer.start()
        return True

    def start_countdown(self):
        now_ts = self._now_ts()
        self.scheduler.start(now_ts=now_ts)
        if self.scheduler.is_running and self._active_run_started_at is None:
            self._active_run_started_at = now_ts
        self._update_countdown_display(now_ts=now_ts)

    def pause_countdown(self):
        now_ts = self._now_ts()
        self._finish_active_run(now_ts=now_ts, end_reason="pause")
        self.scheduler.pause(now_ts=now_ts)
        self._update_countdown_display(now_ts=now_ts)

    def _finish_active_run(self, now_ts, end_reason):
        if self._active_run_started_at is None:
            return
        self.run_history_store.add_record(
            start_at=self._active_run_started_at,
            end_at=now_ts,
            end_reason=end_reason,
        )
        self._active_run_started_at = None
        if self.run_history_dialog is not None:
            self.run_history_dialog.refresh()
        return

    def toggle_countdown(self):
        if self.scheduler.is_running:
            self.pause_countdown()
        else:
            self.start_countdown()

    def reset_countdown(self):
        now_ts = self._now_ts()
        self._finish_active_run(now_ts=now_ts, end_reason="reset")
        self.scheduler.reset(now_ts=now_ts)
        if self.scheduler.is_running:
            self._active_run_started_at = now_ts
        self._update_countdown_display(now_ts=now_ts)

    def _update_countdown_display(self, now_ts):
        if self.scheduler.is_paused:
            remaining_seconds = self.scheduler.remaining_seconds
            self.preview_status_label.setText("已暂停")
        elif self.scheduler.next_due_ts is None:
            remaining_seconds = 0
            self.preview_status_label.setText("距离下次提醒")
        else:
            remaining_seconds = max(0, self.scheduler.next_due_ts - now_ts)
            if remaining_seconds == 0:
                self.preview_status_label.setText("现在该起来活动了")
            else:
                self.preview_status_label.setText("稍后提醒剩余" if self.scheduler.is_snoozed else "距离下次提醒")

        minutes, seconds = divmod(remaining_seconds, 60)
        self.preview_countdown_label.setText(f"{minutes:02d}:{seconds:02d}")
        self.preview_toggle_button.setText("暂停" if self.scheduler.is_running else "开始")

    def _handle_preview_close(self, event: QCloseEvent):
        self.preview_window.hide()
        event.ignore()

    def open_settings_dialog_for_test(self):
        return SettingsDialog(interval_seconds=self.config.interval_seconds)

    def apply_interval_seconds(self, interval_seconds):
        self.config.interval_seconds = interval_seconds
        self.config.save(self.config_path)
        now_ts = self._now_ts()
        self.scheduler.update_interval(self.config.interval_seconds, now_ts=now_ts)
        self._update_countdown_display(now_ts=now_ts)

    def apply_background_key(self, background_key):
        self.config.background_key = background_key
        self.config.save(self.config_path)

    def show_settings_panel(self):
        if self.settings_panel is not None and self.settings_panel.isVisible():
            self.settings_panel.raise_()
            self.settings_panel.activateWindow()
            return self.settings_panel

        self.settings_panel = SettingsPanel(
            interval_seconds=self.config.interval_seconds,
            background_key=self.config.background_key,
        )
        self.settings_panel.interval_changed.connect(self.apply_interval_seconds)
        self.settings_panel.background_changed.connect(self.apply_background_key)
        self.settings_panel.show()
        self.settings_panel.raise_()
        self.settings_panel.activateWindow()
        return self.settings_panel

    def open_settings(self):
        return self.show_settings_panel()

    def show_history_dialog(self):
        if self.history_dialog is not None and self.history_dialog.isVisible():
            self.history_dialog.raise_()
            self.history_dialog.activateWindow()
            return self.history_dialog

        self.history_dialog = HistoryDialog(self.history_markdown_path)
        self.history_dialog.show()
        self.history_dialog.raise_()
        self.history_dialog.activateWindow()
        return self.history_dialog

    def show_run_history_dialog(self):
        if self.run_history_dialog is not None and self.run_history_dialog.isVisible():
            self.run_history_dialog.refresh()
            self.run_history_dialog.raise_()
            self.run_history_dialog.activateWindow()
            return self.run_history_dialog

        self.run_history_dialog = RunHistoryDialog(self.run_history_store)
        self.run_history_dialog.show()
        self.run_history_dialog.raise_()
        self.run_history_dialog.activateWindow()
        return self.run_history_dialog

    def quit_app(self):
        self.check_timer.stop()
        self.tray_icon.hide()
        self.app.quit()

    def _check_due(self):
        now_ts = self._now_ts()
        self._update_countdown_display(now_ts=now_ts)
        if self.scheduler.next_due_ts is None:
            return
        if self.reminder_dialog is not None and self.reminder_dialog.isVisible():
            return
        if self._should_auto_pause(self._system_idle_seconds()):
            self._auto_pause_countdown(now_ts)
            return
        if now_ts < self.scheduler.next_due_ts:
            return

        self.show_reminder_preview()

    def _should_auto_pause(self, idle_seconds, threshold_seconds=5 * 60):
        return self.scheduler.is_running and not self.scheduler.is_paused and idle_seconds >= threshold_seconds

    def _auto_pause_countdown(self, now_ts):
        self._finish_active_run(now_ts=now_ts, end_reason="auto_pause")
        self.scheduler.pause(now_ts=now_ts)
        self._update_countdown_display(now_ts=now_ts)

    def _system_idle_seconds(self):
        if sys.platform != "win32":
            return 0
        user32 = getattr(ctypes, "windll", None)
        kernel32 = getattr(ctypes, "windll", None)
        if user32 is None or kernel32 is None:
            return 0
        info = LASTINPUTINFO()
        info.cbSize = ctypes.sizeof(LASTINPUTINFO)
        if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info)):
            return 0
        now_ms = ctypes.windll.kernel32.GetTickCount64()
        idle_ms = max(0, int(now_ms) - int(info.dwTime))
        return idle_ms // 1000

    def show_reminder_preview(self):
        if self.reminder_dialog is not None and self.reminder_dialog.isVisible():
            return

        self.reminder_dialog = ReminderDialog(background_key=self.config.background_key)
        self.reminder_dialog.action_selected.connect(self._handle_dialog_finished)
        self.reminder_dialog.show()
        self.reminder_dialog.raise_()
        self.reminder_dialog.activateWindow()
        return self.reminder_dialog

    def _handle_dialog_finished(self, _result):
        action = self.reminder_dialog.get_action() if self.reminder_dialog else None
        now_ts = self._now_ts()
        self._finish_active_run(now_ts=now_ts, end_reason=action or "complete")
        if action == "snooze":
            self.scheduler.snooze(now_ts=now_ts)
            self._active_run_started_at = now_ts
        else:
            self.scheduler.complete_reminder(now_ts=now_ts)
            self._active_run_started_at = now_ts
        self._update_countdown_display(now_ts=now_ts)
        self.reminder_dialog = None

    def _build_icon(self):
        return self.app.style().standardIcon(QStyle.SP_ComputerIcon)

    @staticmethod
    def _now_ts():
        return int(time.time())
