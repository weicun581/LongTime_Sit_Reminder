import pathlib
import sys
import unittest
from datetime import datetime
from unittest.mock import MagicMock

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtTest import QTest
from PyQt5.QtGui import QCloseEvent, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QStyle, QSystemTrayIcon

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app_controller import APP_VERSION, AppController


EXPECTED_VERSION = "0.3.0"


class AppControllerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_start_shows_tray_icon(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)
        controller.tray_icon.show = MagicMock()

        started = controller.start()

        self.assertTrue(started)
        controller.tray_icon.show.assert_called_once()

    def test_build_icon_uses_standard_system_icon(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)

        icon = controller._build_icon()
        expected_icon = self.app.style().standardIcon(QStyle.SP_ComputerIcon)

        self.assertIsInstance(icon, QIcon)
        self.assertFalse(icon.isNull())
        self.assertFalse(expected_icon.isNull())
        self.assertFalse(icon.pixmap(16, 16).isNull())
        self.assertFalse(expected_icon.pixmap(16, 16).isNull())

    def test_start_shows_preview_window(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)

        started = controller.start()

        self.assertTrue(started)
        self.assertTrue(controller.preview_window.isVisible())
        self.assertEqual(APP_VERSION, EXPECTED_VERSION)
        self.assertEqual(controller.preview_window.windowTitle(), f"久坐提醒 v{EXPECTED_VERSION}")
        self.assertFalse(controller.preview_window.windowIcon().isNull())

    def test_preview_window_exposes_timer_control_buttons(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)

        self.assertEqual(controller.preview_toggle_button.text(), "开始")
        self.assertEqual(controller.preview_reset_button.text(), "重置")
        self.assertEqual(controller.preview_toggle_shortcut.key().toString(), "Space")

    def test_preview_window_uses_main_window_with_menu_bar(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)

        self.assertIsInstance(controller.preview_window, QMainWindow)
        self.assertIsNotNone(controller.preview_window.menuBar())
        self.assertEqual(APP_VERSION, EXPECTED_VERSION)
        self.assertEqual(controller.preview_window.windowTitle(), f"久坐提醒 v{EXPECTED_VERSION}")

    def test_preview_window_arranges_buttons_without_tabs(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)

        button_layout = controller.preview_button_layout

        self.assertEqual(button_layout.columnCount(), 2)
        self.assertEqual(button_layout.itemAtPosition(0, 0).widget(), controller.preview_toggle_button)
        self.assertEqual(button_layout.itemAtPosition(0, 1).widget(), controller.preview_reset_button)
        self.assertEqual(button_layout.itemAtPosition(1, 0).widget(), controller.preview_reminder_button)
        self.assertEqual(button_layout.itemAtPosition(1, 1), None)
        self.assertEqual(button_layout.itemAtPosition(2, 0), None)
        self.assertEqual(button_layout.itemAtPosition(2, 1), None)
        self.assertFalse(hasattr(controller, "preview_tabs"))
        self.assertEqual(controller.preview_toggle_button.text(), "开始")
        self.assertEqual(controller.preview_reset_button.text(), "重置")
        self.assertEqual(controller.preview_reminder_button.text(), "预览提醒弹窗")

    def test_preview_window_keeps_main_buttons_in_central_widget(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)

        central_widget = controller.preview_window.centralWidget()

        self.assertEqual(controller.preview_toggle_button.parent(), central_widget)
        self.assertEqual(controller.preview_reset_button.parent(), central_widget)
        self.assertEqual(controller.preview_reminder_button.parent(), central_widget)

    def test_menu_bar_exposes_settings_and_history_actions(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)

        menu_actions = controller.preview_window.menuBar().actions()
        menu_texts = [action.text() for action in menu_actions]

        self.assertIn("设置", menu_texts)
        self.assertIn("历史版本", menu_texts)
        self.assertIn("运行记录", menu_texts)

    def test_settings_action_is_attached_to_menu_bar(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)

        self.assertEqual(controller.preview_settings_action.text(), "设置")
        self.assertIn(controller.preview_settings_action, controller.preview_window.menuBar().actions())

    def test_settings_action_opens_settings_panel_window(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)

        panel = controller.show_settings_panel()

        self.assertIsNotNone(panel)
        self.assertEqual(panel.windowTitle(), "设置")
        self.assertEqual(panel.timer_button.text(), "计时器")
        self.assertEqual(panel.background_button.text(), "更换提醒背景")
        panel.close()
        self.app.processEvents()

    def test_history_action_is_attached_to_menu_bar(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)

        self.assertEqual(controller.preview_history_action.text(), "历史版本")
        self.assertIn(controller.preview_history_action, controller.preview_window.menuBar().actions())

    def test_run_history_action_is_attached_to_menu_bar(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)

        self.assertEqual(controller.preview_run_history_action.text(), "运行记录")
        self.assertIn(controller.preview_run_history_action, controller.preview_window.menuBar().actions())

    def test_menu_bar_is_part_of_preview_window(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)

        self.assertEqual(controller.preview_window.menuBar().parent(), controller.preview_window)
        self.assertIsNotNone(controller.preview_window.centralWidget())
        self.assertEqual(controller.preview_window.centralWidget().parent(), controller.preview_window)

    def test_preview_window_central_widget_has_main_layout(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)

        central_layout = controller.preview_window.centralWidget().layout()

        self.assertIsNotNone(central_layout)
        self.assertGreaterEqual(central_layout.count(), 4)
        self.assertEqual(central_layout.itemAt(central_layout.count() - 1).layout(), controller.preview_button_layout)

    def test_menu_bar_history_action_opens_history_dialog(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)

        controller.preview_history_action.trigger()

        self.assertIsNotNone(controller.history_dialog)
        self.assertTrue(controller.history_dialog.isVisible())
        controller.history_dialog.close()
        self.app.processEvents()

    def test_menu_bar_settings_action_opens_settings_panel_window(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)

        controller.preview_settings_action.trigger()

        self.assertIsNotNone(controller.settings_panel)
        self.assertTrue(controller.settings_panel.isVisible())
        controller.settings_panel.close()
        self.app.processEvents()

    def test_history_dialog_reloads_markdown_from_shared_source(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)

        dialog = controller.show_history_dialog()

        self.assertIn("# 更新历史", dialog.toMarkdown())
        dialog.close()
        self.app.processEvents()

    def test_preview_window_has_no_embedded_history_view(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)

        self.assertFalse(hasattr(controller, "preview_history_view"))

    def test_tray_menu_exposes_history_action(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)

        self.assertEqual(controller.tray_icon.history_action.text(), "历史版本")

    def test_run_history_action_opens_run_history_dialog(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)

        controller.preview_run_history_action.trigger()

        self.assertIsNotNone(controller.run_history_dialog)
        self.assertTrue(controller.run_history_dialog.isVisible())
        self.assertEqual(controller.run_history_dialog.windowTitle(), "运行记录")
        controller.run_history_dialog.close()
        self.app.processEvents()

    def test_start_and_pause_record_run_segment(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)
        controller._now_ts = MagicMock(side_effect=[100, 160])

        controller.start_countdown()
        controller.pause_countdown()

        self.assertEqual(len(controller.run_history_store.records), 1)
        record = controller.run_history_store.records[0]
        self.assertEqual(record["start_at"], 100)
        self.assertEqual(record["end_at"], 160)
        self.assertEqual(record["duration_seconds"], 60)
        self.assertEqual(record["end_reason"], "pause")

    def test_reset_records_run_segment(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)
        controller._now_ts = MagicMock(side_effect=[200, 245])

        controller.start_countdown()
        controller.reset_countdown()

        self.assertEqual(len(controller.run_history_store.records), 1)
        record = controller.run_history_store.records[0]
        self.assertEqual(record["start_at"], 200)
        self.assertEqual(record["end_at"], 245)
        self.assertEqual(record["duration_seconds"], 45)
        self.assertEqual(record["end_reason"], "reset")

    def test_run_history_dialog_shows_today_total_and_records(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)
        controller.run_history_store.records = [
            {
                "start_at": 1748448000,
                "end_at": 1748448060,
                "duration_seconds": 60,
                "end_reason": "pause",
            },
            {
                "start_at": 1748448120,
                "end_at": 1748448240,
                "duration_seconds": 120,
                "end_reason": "reset",
            },
        ]

        dialog = controller.show_run_history_dialog()

        text = dialog.toPlainText()

        self.assertIn("今日累计：00:03:00", text)
        self.assertIn(datetime.fromtimestamp(1748448000).strftime("%Y-%m-%d"), text)
        self.assertIn(datetime.fromtimestamp(1748448000).strftime("%H:%M:%S"), text)
        self.assertIn(datetime.fromtimestamp(1748448240).strftime("%H:%M:%S"), text)
        self.assertIn("暂停", text)
        self.assertIn("重置", text)
        dialog.close()
        self.app.processEvents()

    def test_run_history_dialog_groups_multiple_days(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)
        controller.run_history_store.records = [
            {
                "start_at": 1748361600,
                "end_at": 1748361660,
                "duration_seconds": 60,
                "end_reason": "pause",
            },
            {
                "start_at": 1748448000,
                "end_at": 1748448180,
                "duration_seconds": 180,
                "end_reason": "complete",
            },
        ]

        dialog = controller.show_run_history_dialog()
        text = dialog.toPlainText()

        self.assertIn(datetime.fromtimestamp(1748361600).strftime("%Y-%m-%d"), text)
        self.assertIn(datetime.fromtimestamp(1748448000).strftime("%Y-%m-%d"), text)
        self.assertIn("完成", text)
        dialog.close()
        self.app.processEvents()

    def test_complete_reminder_records_run_segment(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)
        controller.start_countdown()
        controller._active_run_started_at = 300
        controller.reminder_dialog = MagicMock()
        controller.reminder_dialog.get_action.return_value = "complete"
        controller._now_ts = MagicMock(return_value=360)

        controller._handle_dialog_finished("complete")

        self.assertEqual(len(controller.run_history_store.records), 1)
        record = controller.run_history_store.records[0]
        self.assertEqual(record["start_at"], 300)
        self.assertEqual(record["end_at"], 360)
        self.assertEqual(record["duration_seconds"], 60)
        self.assertEqual(record["end_reason"], "complete")

    def test_run_history_dialog_translates_complete_reason(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)
        controller.run_history_store.records = [
            {
                "start_at": 1748448000,
                "end_at": 1748448060,
                "duration_seconds": 60,
                "end_reason": "complete",
            }
        ]

        dialog = controller.show_run_history_dialog()

        self.assertIn("完成", dialog.toPlainText())
        self.assertNotIn("complete", dialog.toPlainText())
        dialog.close()
        self.app.processEvents()

    def test_history_action_opens_history_dialog(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)

        dialog = controller.show_history_dialog()

        self.assertIsNotNone(dialog)
        self.assertEqual(dialog.windowTitle(), "历史版本")
        self.assertTrue(dialog.isReadOnly())
        self.assertIn("# 更新历史", dialog.toMarkdown())
        dialog.close()
        self.app.processEvents()

    def test_tray_history_action_opens_history_dialog(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)

        controller.tray_icon.history_action.trigger()

        self.assertIsNotNone(controller.history_dialog)
        self.assertTrue(controller.history_dialog.isVisible())
        controller.history_dialog.close()
        self.app.processEvents()

    def test_double_clicking_tray_icon_shows_main_page(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)
        controller.preview_window.show = MagicMock()
        controller.preview_window.raise_ = MagicMock()
        controller.preview_window.activateWindow = MagicMock()

        controller.tray_icon.activated.emit(QSystemTrayIcon.DoubleClick)

        controller.preview_window.show.assert_called_once()
        controller.preview_window.raise_.assert_called_once()
        controller.preview_window.activateWindow.assert_called_once()

    def test_history_dialog_shows_default_message_when_file_is_missing(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)
        controller.history_markdown_path = PROJECT_ROOT / "res" / "missing_version_history.md"

        dialog = controller.show_history_dialog()

        self.assertIn("暂无历史版本记录", dialog.toPlainText())
        self.assertTrue(dialog.isReadOnly())
        dialog.close()
        self.app.processEvents()

    def test_history_dialog_reuses_existing_visible_window(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)

        first_dialog = controller.show_history_dialog()
        second_dialog = controller.show_history_dialog()

        self.assertIs(first_dialog, second_dialog)
        first_dialog.close()
        self.app.processEvents()

    def test_settings_dialog_uses_single_row_time_inputs_layout(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)

        dialog = controller.open_settings_dialog_for_test()

        self.assertEqual(dialog.time_input_layout.count(), 6)
        self.assertEqual(dialog.time_input_layout.itemAt(0).widget(), dialog.hours_input)
        self.assertEqual(dialog.time_input_layout.itemAt(1).widget(), dialog.hours_unit_label)
        self.assertEqual(dialog.time_input_layout.itemAt(2).widget(), dialog.minutes_input)
        self.assertEqual(dialog.time_input_layout.itemAt(3).widget(), dialog.minutes_unit_label)
        self.assertEqual(dialog.time_input_layout.itemAt(4).widget(), dialog.seconds_input)
        self.assertEqual(dialog.time_input_layout.itemAt(5).widget(), dialog.seconds_unit_label)
        self.assertEqual(dialog.time_form_layout.rowCount(), 1)
        dialog.close()

    def test_history_markdown_path_points_to_res_directory(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)

        self.assertEqual(controller.history_markdown_path, PROJECT_ROOT / "res" / "version_history.md")
        self.assertEqual(controller.history_markdown_path.name, "version_history.md")
        self.assertEqual(controller.history_markdown_path.parent.name, "res")

    def test_due_state_opens_full_screen_green_reminder_overlay(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)
        controller.start()
        controller.scheduler.next_due_ts = 100
        controller.scheduler.is_snoozed = False
        controller._now_ts = MagicMock(return_value=100)

        controller._check_due()
        self.app.processEvents()

        screen_geometry = self.app.primaryScreen().geometry()

        self.assertIsNotNone(controller.reminder_dialog)
        self.assertTrue(controller.reminder_dialog.windowState() & Qt.WindowFullScreen)
        self.assertEqual(controller.reminder_dialog.geometry(), screen_geometry)
        self.assertEqual(controller.reminder_dialog.frameGeometry(), screen_geometry)
        self.assertTrue(controller.reminder_dialog.windowFlags() & Qt.WindowStaysOnTopHint)
        self.assertTrue(controller.reminder_dialog.has_grass_image())
        self.assertTrue(controller.reminder_dialog.image_label.pixmap() is not None)
        self.assertTrue(controller.reminder_dialog.testAttribute(Qt.WA_DeleteOnClose))
        self.assertTrue(controller.reminder_dialog.click_to_close_enabled())
        self.assertTrue(controller.reminder_dialog.runtime_overlay_snapshot()["is_full_screen"])
        self.assertTrue(controller.reminder_dialog.runtime_overlay_snapshot()["is_visible"])
        self.assertTrue(controller.reminder_dialog.runtime_overlay_snapshot()["stays_on_top"])
        self.assertTrue(controller.reminder_dialog.runtime_overlay_snapshot()["has_image"])
        self.assertTrue(controller.reminder_dialog.runtime_overlay_snapshot()["click_to_close_enabled"])
        self.assertTrue(controller.reminder_dialog.runtime_overlay_snapshot()["has_translucent_style"])
        self.assertEqual(controller.reminder_dialog.windowTitle(), "久坐提醒")
        self.assertTrue(controller.reminder_dialog.testAttribute(Qt.WA_TranslucentBackground))
        self.assertTrue(controller.reminder_dialog.testAttribute(Qt.WA_DeleteOnClose))
        self.assertEqual(controller.preview_status_label.text(), "现在该起来活动了")
        self.assertEqual(controller.preview_countdown_label.text(), "00:00")
        self.assertEqual(
            controller.reminder_dialog.runtime_overlay_snapshot()["geometry"],
            screen_geometry.getRect(),
        )
        self.assertEqual(
            controller.reminder_dialog.runtime_overlay_snapshot()["frame_geometry"],
            screen_geometry.getRect(),
        )

    def test_reminder_overlay_click_restarts_full_interval(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)
        controller.start()
        controller.scheduler.next_due_ts = 100
        controller._now_ts = MagicMock(side_effect=[100, 150])

        controller._check_due()
        controller.reminder_dialog.action_selected.emit("complete")

        self.assertIsNone(controller.reminder_dialog)
        self.assertEqual(controller.scheduler.next_due_ts, 150 + controller.scheduler.configured_duration_seconds)
        self.assertEqual(controller.preview_status_label.text(), "距离下次提醒")
        self.assertFalse(controller.scheduler.is_snoozed)
        self.assertFalse(controller.scheduler.is_paused)
        self.assertTrue(controller.scheduler.is_running)

    def test_reminder_overlay_escape_restarts_full_interval(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)
        controller.start()
        controller.scheduler.next_due_ts = 100
        controller._now_ts = MagicMock(side_effect=[100, 150])

        controller._check_due()
        controller.reminder_dialog.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_Escape, Qt.NoModifier))

        self.assertIsNone(controller.reminder_dialog)
        self.assertEqual(controller.scheduler.next_due_ts, 150 + controller.scheduler.configured_duration_seconds)
        self.assertEqual(controller.preview_status_label.text(), "距离下次提醒")
        self.assertFalse(controller.scheduler.is_snoozed)
        self.assertFalse(controller.scheduler.is_paused)
        self.assertTrue(controller.scheduler.is_running)

    def test_reminder_dialog_shows_grass_image(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)

        dialog = controller.show_reminder_preview()
        snapshot = dialog.runtime_overlay_snapshot()

        self.assertTrue(dialog.has_grass_image())
        self.assertIsNotNone(dialog.image_label.pixmap())
        self.assertTrue(dialog.click_to_close_enabled())
        self.assertEqual(dialog.windowTitle(), "久坐提醒")
        self.assertIsNone(dialog.get_action())
        self.assertIsNone(dialog.result())
        self.assertEqual(dialog.image_label.objectName(), "grassImageLabel")
        self.assertEqual(dialog.image_label.parent(), dialog)
        self.assertTrue(dialog.testAttribute(Qt.WA_TranslucentBackground))
        self.assertTrue(dialog.testAttribute(Qt.WA_DeleteOnClose))
        self.assertTrue(dialog.windowFlags() & Qt.WindowStaysOnTopHint)
        self.assertTrue(dialog.windowFlags() & Qt.FramelessWindowHint)
        self.assertTrue(dialog.windowFlags() & Qt.Tool)
        self.assertTrue(dialog.windowFlags() & Qt.Window)
        self.assertEqual(dialog.windowState() & Qt.WindowFullScreen, Qt.WindowFullScreen)
        self.assertIsNotNone(dialog.overlay_label)
        self.assertFalse(dialog.overlay_label.isHidden())
        self.assertEqual(dialog.overlay_label.geometry(), dialog.rect())
        self.assertIn("grassImageLabel", dialog.styleSheet())
        self.assertEqual(dialog.geometry(), self.app.primaryScreen().geometry())
        self.assertEqual(dialog.frameGeometry(), self.app.primaryScreen().geometry())
        self.assertTrue(snapshot["has_image"])
        self.assertTrue(snapshot["click_to_close_enabled"])
        self.assertTrue(snapshot["has_translucent_style"])
        self.assertTrue(snapshot["stays_on_top"])
        self.assertTrue(snapshot["is_full_screen"])
        self.assertTrue(snapshot["is_visible"])
        self.assertEqual(snapshot["geometry"], self.app.primaryScreen().geometry().getRect())
        self.assertEqual(snapshot["frame_geometry"], self.app.primaryScreen().geometry().getRect())

    def test_reminder_dialog_shows_due_state_message(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)

        dialog = controller.show_reminder_preview()

        self.assertTrue(dialog.has_grass_image())
        self.assertIsNotNone(dialog.image_label.pixmap())
        self.assertIsNone(dialog.get_action())
        self.assertIsNone(dialog.result())
        self.assertFalse(hasattr(dialog, "status_label"))
        self.assertFalse(hasattr(dialog, "message_label"))
        self.assertFalse(hasattr(dialog, "close_button"))
        self.assertFalse(hasattr(dialog, "snooze_button"))
        self.assertFalse(dialog.inherits("QDialog"))
        self.assertTrue(dialog.inherits("QWidget"))
        self.assertTrue(dialog.runtime_overlay_snapshot()["has_image"])
        self.assertTrue(dialog.runtime_overlay_snapshot()["click_to_close_enabled"])
        self.assertTrue(dialog.runtime_overlay_snapshot()["is_full_screen"])
        self.assertTrue(dialog.runtime_overlay_snapshot()["is_visible"])
        self.assertEqual(dialog.geometry(), self.app.primaryScreen().geometry())
        self.assertEqual(dialog.frameGeometry(), self.app.primaryScreen().geometry())
        self.assertEqual(dialog.windowTitle(), "久坐提醒")
        self.assertEqual(dialog.image_label.objectName(), "grassImageLabel")
        self.assertTrue(dialog.click_to_close_enabled())
        self.assertTrue(dialog.windowFlags() & Qt.WindowStaysOnTopHint)
        self.assertEqual(dialog.windowState() & Qt.WindowFullScreen, Qt.WindowFullScreen)
        self.assertTrue(dialog.testAttribute(Qt.WA_TranslucentBackground))
        self.assertTrue(dialog.testAttribute(Qt.WA_DeleteOnClose))
        self.assertFalse(dialog.autoFillBackground())
        self.assertIn("grassImageLabel", dialog.styleSheet())
        self.assertIn("overlayLabel", dialog.styleSheet())
        self.assertIn("rgba(34, 197, 94, 110)", dialog.styleSheet())
        self.assertEqual(dialog.runtime_overlay_snapshot()["geometry"], self.app.primaryScreen().geometry().getRect())
        self.assertEqual(dialog.runtime_overlay_snapshot()["frame_geometry"], self.app.primaryScreen().geometry().getRect())
        self.assertTrue(hasattr(dialog, "image_label"))
        self.assertTrue(hasattr(dialog, "action_selected"))
        self.assertTrue(hasattr(dialog, "Accepted"))
        self.assertTrue(callable(dialog.get_action))
        self.assertTrue(callable(dialog.runtime_overlay_snapshot))
        self.assertTrue(callable(dialog.has_grass_image))
        self.assertTrue(callable(dialog.click_to_close_enabled))
        self.assertTrue(callable(dialog.mousePressEvent))
        self.assertTrue(callable(dialog.keyPressEvent))
        self.assertTrue(callable(dialog.resizeEvent))
        self.assertTrue(callable(dialog.showEvent))
        self.assertTrue(callable(dialog._apply_primary_screen_geometry))
        self.assertTrue(callable(dialog._refresh_scaled_pixmap))

    def test_apply_interval_change_refreshes_countdown_after_interval_change(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)
        controller.start()
        controller._now_ts = MagicMock(return_value=100)
        controller.config.save = MagicMock()

        controller.apply_interval_seconds(45 * 60)

        self.assertEqual(controller.preview_countdown_label.text(), "45:00")
        self.assertEqual(controller.config.interval_seconds, 2700)
        self.assertEqual(controller.scheduler.configured_duration_seconds, 2700)
        self.assertEqual(controller.scheduler.remaining_seconds, 2700)
        self.assertEqual(controller.scheduler.next_due_ts, 2800)
        self.assertTrue(controller.scheduler.is_running)
        self.assertFalse(controller.scheduler.is_paused)
        self.assertFalse(controller.scheduler.is_snoozed)
        controller.config.save.assert_called_once_with(controller.config_path)

    def test_preview_window_exposes_reminder_actions_and_menu_bar(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)

        controller.start()

        self.assertIsNotNone(controller.preview_window.menuBar())
        self.assertIsNotNone(controller.preview_settings_action)
        self.assertIsNotNone(controller.preview_history_action)
        self.assertIsNotNone(controller.preview_reminder_button)
        self.assertEqual(controller.preview_reminder_button.text(), "预览提醒弹窗")
        self.assertEqual(controller.preview_toggle_button.text(), "暂停")
        self.assertEqual(controller.preview_reset_button.text(), "重置")
        self.assertEqual(controller.preview_toggle_button.objectName(), "primaryActionButton")
        self.assertEqual(controller.preview_reset_button.objectName(), "secondaryActionButton")
        self.assertFalse(controller.preview_window.windowIcon().isNull())
        self.assertEqual(controller.preview_window.windowTitle(), f"久坐提醒 v{APP_VERSION}")
        self.assertIsNotNone(controller.preview_window.centralWidget())
        self.assertIsNotNone(controller.preview_window.centralWidget().layout())
        self.assertGreaterEqual(controller.preview_window.centralWidget().layout().count(), 4)
        self.assertIsNotNone(controller.preview_button_layout)
        self.assertEqual(controller.preview_status_label.text(), "距离下次提醒")
        self.assertRegex(controller.preview_countdown_label.text(), r"\d{2}:\d{2}")
        self.assertTrue(controller.preview_toggle_button.isEnabled())
        self.assertTrue(controller.preview_reset_button.isEnabled())
        self.assertEqual(controller.preview_toggle_button.parent(), controller.preview_window.centralWidget())
        self.assertEqual(controller.preview_reset_button.parent(), controller.preview_window.centralWidget())
        self.assertEqual(controller.preview_reminder_button.parent(), controller.preview_window.centralWidget())
        self.assertTrue(isinstance(controller.preview_toggle_button.text(), str))
        self.assertTrue(isinstance(controller.preview_reset_button.text(), str))
        self.assertEqual(controller.preview_toggle_button.text().strip(), "暂停")
        self.assertEqual(controller.preview_reset_button.text().strip(), "重置")
        self.assertGreater(controller.preview_toggle_button.minimumHeight(), 0)
        self.assertGreater(controller.preview_reset_button.minimumHeight(), 0)
        self.assertGreaterEqual(controller.preview_window.minimumWidth(), 420)
        self.assertEqual(controller.preview_status_label.objectName(), "previewStatusLabel")
        self.assertEqual(controller.preview_countdown_label.objectName(), "previewCountdownLabel")
        self.assertIn("QPushButton", controller.preview_window.centralWidget().styleSheet())
        self.assertIn("#primaryActionButton", controller.preview_window.centralWidget().styleSheet())
        self.assertIn("#secondaryActionButton", controller.preview_window.centralWidget().styleSheet())

    def test_toggle_button_freezes_remaining_time(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)
        controller.scheduler.update_interval(interval_seconds=60, now_ts=0)
        controller._now_ts = MagicMock(side_effect=[100, 130, 130])

        controller.preview_reset_button.click()
        controller.preview_toggle_button.click()
        frozen_value = controller.preview_countdown_label.text()
        controller._check_due()

        self.assertEqual(controller.preview_countdown_label.text(), frozen_value)
        self.assertTrue(controller.scheduler.is_paused)
        self.assertFalse(controller.scheduler.is_running)
        self.assertEqual(controller.scheduler.remaining_seconds, 30)
        self.assertEqual(controller.preview_status_label.text(), "已暂停")
        self.assertEqual(controller.preview_countdown_label.text(), "00:30")
        self.assertEqual(controller.preview_toggle_button.text(), "开始")
        self.assertIsNone(controller.scheduler.next_due_ts)
        self.assertIsNone(controller.reminder_dialog)

    def test_space_shortcut_toggles_countdown_state(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)
        controller.start()
        controller._now_ts = MagicMock(side_effect=[100, 120])
        controller.preview_window.activateWindow()
        controller.preview_window.setFocus()
        self.app.processEvents()

        QTest.keyClick(controller.preview_window, Qt.Key_Space)

        self.assertTrue(controller.scheduler.is_paused)
        self.assertEqual(controller.preview_toggle_button.text(), "开始")

        QTest.keyClick(controller.preview_window, Qt.Key_Space)

        self.assertTrue(controller.scheduler.is_running)
        self.assertFalse(controller.scheduler.is_paused)
        self.assertEqual(controller.preview_toggle_button.text(), "暂停")

    def test_apply_interval_seconds_applies_second_based_duration(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)
        controller.start()
        controller._now_ts = MagicMock(return_value=100)

        controller.apply_interval_seconds(3723)

        self.assertEqual(controller.preview_countdown_label.text(), "62:03")
        self.assertEqual(controller.config.interval_seconds, 3723)
        self.assertEqual(controller.scheduler.configured_duration_seconds, 3723)
        self.assertTrue(controller.scheduler.is_running)
        self.assertFalse(controller.scheduler.is_paused)
        self.assertEqual(controller.preview_status_label.text(), "距离下次提醒")
        self.assertEqual(controller.scheduler.next_due_ts, 3823)

    def test_countdown_updates_for_normal_and_snooze_states(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)
        controller.start()

        controller.scheduler.next_due_ts = 130
        controller._update_countdown_display(now_ts=100)
        self.assertEqual(controller.preview_status_label.text(), "距离下次提醒")
        self.assertEqual(controller.preview_countdown_label.text(), "00:30")

        controller.scheduler.is_snoozed = True
        controller._update_countdown_display(now_ts=100)
        self.assertEqual(controller.preview_status_label.text(), "稍后提醒剩余")
        self.assertEqual(controller.preview_countdown_label.text(), "00:30")

    def test_due_state_shows_zero_countdown(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)
        controller.start()

        controller.scheduler.next_due_ts = 100
        controller.scheduler.is_snoozed = False
        controller._update_countdown_display(now_ts=100)

        self.assertEqual(controller.preview_status_label.text(), "现在该起来活动了")
        self.assertEqual(controller.preview_countdown_label.text(), "00:00")

    def test_check_due_refreshes_countdown_every_second(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)
        controller.start()
        controller.scheduler.next_due_ts = 165
        controller.scheduler.is_snoozed = False
        controller._now_ts = MagicMock(side_effect=[100, 101])

        controller._check_due()
        first_value = controller.preview_countdown_label.text()

        controller._check_due()
        second_value = controller.preview_countdown_label.text()

        self.assertEqual(first_value, "01:05")
        self.assertEqual(second_value, "01:04")

    def test_show_main_page_displays_preview_window(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)
        controller.preview_window.show = MagicMock()
        controller.preview_window.raise_ = MagicMock()
        controller.preview_window.activateWindow = MagicMock()

        controller.show_main_page()

        controller.preview_window.show.assert_called_once()
        controller.preview_window.raise_.assert_called_once()
        controller.preview_window.activateWindow.assert_called_once()

    def test_start_brings_preview_window_to_front(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)
        controller.preview_window.raise_ = MagicMock()
        controller.preview_window.activateWindow = MagicMock()

        controller.start()

        controller.preview_window.raise_.assert_called_once()
        controller.preview_window.activateWindow.assert_called_once()
        self.assertFalse(controller.preview_window.isMinimized())

    def test_tray_show_main_page_action_uses_show_main_page(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)
        controller.preview_window.hide()

        controller.tray_icon.show_main_page_action.trigger()

        self.assertTrue(controller.preview_window.isVisible())
        self.assertEqual(controller.preview_status_label.text(), "距离下次提醒")
        self.assertRegex(controller.preview_countdown_label.text(), r"\d{2}:\d{2}")

    def test_start_disables_quit_on_last_window_closed(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)
        self.app.setQuitOnLastWindowClosed(True)

        controller.start()

        self.assertFalse(self.app.quitOnLastWindowClosed())

    def test_preview_window_close_hides_instead_of_exiting(self):
        controller = AppController(app=self.app, base_dir=PROJECT_ROOT)
        controller.start()

        close_event = QCloseEvent()
        controller.preview_window.closeEvent(close_event)

        self.assertTrue(controller.preview_window.isHidden())
        self.assertFalse(close_event.isAccepted())


if __name__ == "__main__":
    unittest.main()
