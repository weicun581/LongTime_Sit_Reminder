import pathlib
import sys
import unittest

from PyQt5.QtCore import QEvent, QPoint, Qt
from PyQt5.QtGui import QKeyEvent, QMouseEvent
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import AppConfig
from reminder_dialog import ReminderDialog
from run_history import RunHistoryStore
from settings_dialog import SettingsDialog


class SettingsDialogTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_save_rejects_zero_total_duration(self):
        dialog = SettingsDialog(interval_seconds=60)
        dialog.hours_input.setText("0")
        dialog.minutes_input.setText("0")
        dialog.seconds_input.setText("0")

        accepted = dialog.try_accept()

        self.assertFalse(accepted)
        self.assertEqual(dialog.error_label.text(), "请输入大于 0 的提醒时长")

    def test_save_accepts_valid_hour_minute_second_values(self):
        dialog = SettingsDialog(interval_seconds=60)
        dialog.hours_input.setText("1")
        dialog.minutes_input.setText("2")
        dialog.seconds_input.setText("3")

        accepted = dialog.try_accept()

        self.assertTrue(accepted)
        self.assertEqual(dialog.get_interval_seconds(), 3723)

    def test_settings_dialog_exposes_hour_minute_and_second_inputs(self):
        dialog = SettingsDialog(interval_seconds=3661)

        self.assertEqual(dialog.hours_input.text(), "1")
        self.assertEqual(dialog.minutes_input.text(), "1")
        self.assertEqual(dialog.seconds_input.text(), "1")
        self.assertEqual(dialog.error_label.objectName(), "settingsErrorLabel")
        self.assertEqual(dialog.hours_input.objectName(), "settingsHoursInput")
        self.assertEqual(dialog.minutes_input.objectName(), "settingsMinutesInput")
        self.assertEqual(dialog.seconds_input.objectName(), "settingsSecondsInput")
        self.assertIsInstance(dialog.time_input_layout, QHBoxLayout)
        self.assertEqual(dialog.time_input_layout.count(), 6)
        self.assertEqual(dialog.time_input_layout.itemAt(0).widget(), dialog.hours_input)
        self.assertEqual(dialog.time_input_layout.itemAt(1).widget(), dialog.hours_unit_label)
        self.assertEqual(dialog.time_input_layout.itemAt(2).widget(), dialog.minutes_input)
        self.assertEqual(dialog.time_input_layout.itemAt(3).widget(), dialog.minutes_unit_label)
        self.assertEqual(dialog.time_input_layout.itemAt(4).widget(), dialog.seconds_input)
        self.assertEqual(dialog.time_input_layout.itemAt(5).widget(), dialog.seconds_unit_label)
        self.assertIsInstance(dialog.hours_unit_label, QLabel)
        self.assertIsInstance(dialog.minutes_unit_label, QLabel)
        self.assertIsInstance(dialog.seconds_unit_label, QLabel)
        self.assertEqual(dialog.hours_unit_label.text(), "小时")
        self.assertEqual(dialog.minutes_unit_label.text(), "分钟")
        self.assertEqual(dialog.seconds_unit_label.text(), "秒")
        self.assertEqual(dialog.minimumWidth(), 300)
        self.assertEqual(dialog.hours_input.maximumWidth(), 70)
        self.assertEqual(dialog.minutes_input.maximumWidth(), 70)
        self.assertEqual(dialog.seconds_input.maximumWidth(), 70)
        self.assertEqual(dialog.time_form_layout.rowCount(), 1)
        self.assertEqual(dialog.time_form_layout.itemAt(1).widget(), dialog.time_input_container)
        self.assertEqual(dialog.time_input_container.layout(), dialog.time_input_layout)
        self.assertEqual(dialog.time_input_container.parent(), dialog)
        self.assertGreaterEqual(dialog.time_input_layout.spacing(), 0)

    def test_settings_dialog_rejects_minute_or_second_above_59(self):
        dialog = SettingsDialog(interval_seconds=60)
        dialog.hours_input.setText("0")
        dialog.minutes_input.setText("61")
        dialog.seconds_input.setText("0")

        accepted = dialog.try_accept()

        self.assertFalse(accepted)
        self.assertEqual(dialog.error_label.text(), "分钟和秒必须在 0 到 59 之间")

    def test_settings_dialog_rejects_negative_values(self):
        dialog = SettingsDialog(interval_seconds=60)
        dialog.hours_input.setText("-1")
        dialog.minutes_input.setText("0")
        dialog.seconds_input.setText("0")

        accepted = dialog.try_accept()

        self.assertFalse(accepted)
        self.assertEqual(dialog.error_label.text(), "请输入非负整数")

    def test_settings_dialog_rejects_non_integer_values(self):
        dialog = SettingsDialog(interval_seconds=60)
        dialog.hours_input.setText("a")
        dialog.minutes_input.setText("0")
        dialog.seconds_input.setText("0")

        accepted = dialog.try_accept()

        self.assertFalse(accepted)
        self.assertEqual(dialog.error_label.text(), "请输入非负整数")

    def test_config_defaults_include_background_and_ini_support(self):
        config = AppConfig.load(PROJECT_ROOT / "missing_config.ini")

        self.assertEqual(config.interval_seconds, 3600)
        self.assertEqual(config.background_key, "image1")

    def test_reminder_dialog_uses_named_widgets_for_polish(self):
        dialog = ReminderDialog()

        self.assertEqual(dialog.image_label.objectName(), "grassImageLabel")

    def test_reminder_dialog_has_packaged_background_image(self):
        dialog = ReminderDialog()

        self.assertTrue(dialog.has_grass_image())
        self.assertIsNotNone(dialog.image_label.pixmap())

    def test_reminder_dialog_uses_full_screen_grass_image_presentation(self):
        dialog = ReminderDialog()

        self.assertEqual(dialog.windowState() & Qt.WindowFullScreen, Qt.WindowFullScreen)
        self.assertTrue(dialog.windowFlags() & Qt.WindowStaysOnTopHint)
        self.assertFalse(dialog.inherits("QDialog"))
        self.assertFalse(dialog.autoFillBackground())
        self.assertTrue(dialog.has_grass_image())
        self.assertIsNotNone(dialog.image_label.pixmap())
        self.assertEqual(dialog.windowTitle(), "久坐提醒")
        self.assertTrue(dialog.testAttribute(Qt.WA_TranslucentBackground))
        self.assertTrue(dialog.testAttribute(Qt.WA_DeleteOnClose))
        self.assertTrue(dialog.click_to_close_enabled())
        self.assertIn("QWidget", dialog.styleSheet())
        self.assertIn("grassImageLabel", dialog.styleSheet())
        self.assertEqual(dialog.image_label.parent(), dialog)
        self.assertEqual(dialog.overlay_label.parent(), dialog)
        self.assertFalse(dialog.overlay_label.isHidden())
        self.assertEqual(dialog.overlay_label.geometry(), dialog.rect())
        self.assertTrue(dialog.runtime_overlay_snapshot()["has_image"])
        self.assertTrue(dialog.runtime_overlay_snapshot()["click_to_close_enabled"])
        self.assertTrue(dialog.runtime_overlay_snapshot()["has_translucent_style"])
        self.assertTrue(dialog.runtime_overlay_snapshot()["has_overlay_label"])
        self.assertEqual(dialog.selected_background_key(), "image1")

    def test_reminder_dialog_click_marks_complete_action(self):
        dialog = ReminderDialog()
        dialog.show()
        self.app.processEvents()

        event = QMouseEvent(
            QEvent.MouseButtonPress,
            QPoint(10, 10),
            Qt.LeftButton,
            Qt.LeftButton,
            Qt.NoModifier,
        )
        dialog.mousePressEvent(event)

        self.assertEqual(dialog.get_action(), "complete")
        self.assertEqual(dialog.result(), dialog.Accepted)

    def test_reminder_dialog_escape_marks_complete_action(self):
        dialog = ReminderDialog()
        dialog.show()
        self.app.processEvents()

        dialog.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_Escape, Qt.NoModifier))

        self.assertEqual(dialog.get_action(), "complete")
        self.assertEqual(dialog.result(), dialog.Accepted)

    def test_reminder_dialog_covers_primary_screen_after_show(self):
        dialog = ReminderDialog()
        dialog.show()
        self.app.processEvents()

        screen_geometry = self.app.primaryScreen().geometry()

        self.assertEqual(dialog.geometry(), screen_geometry)
        self.assertEqual(dialog.frameGeometry(), screen_geometry)

        dialog.close()
        self.app.processEvents()

    def test_reminder_dialog_runtime_snapshot_matches_image_overlay_mode(self):
        dialog = ReminderDialog()

        snapshot = dialog.runtime_overlay_snapshot()

        self.assertEqual(dialog.windowTitle(), "久坐提醒")
        self.assertIsNone(dialog.get_action())
        self.assertIsNone(dialog.result())
        self.assertFalse(dialog.autoFillBackground())
        self.assertTrue(dialog.testAttribute(Qt.WA_TranslucentBackground))
        self.assertTrue(dialog.testAttribute(Qt.WA_DeleteOnClose))
        self.assertTrue(dialog.windowFlags() & Qt.WindowStaysOnTopHint)
        self.assertTrue(dialog.windowFlags() & Qt.FramelessWindowHint)
        self.assertTrue(dialog.windowFlags() & Qt.Tool)
        self.assertEqual(dialog.windowState() & Qt.WindowFullScreen, Qt.WindowFullScreen)
        self.assertEqual(snapshot["has_image"], dialog.has_grass_image())
        self.assertTrue(snapshot["click_to_close_enabled"])
        self.assertTrue(snapshot["has_translucent_style"])
        self.assertTrue(snapshot["has_overlay_label"])
        self.assertEqual(snapshot["background_key"], "image1")
        self.assertEqual(len(snapshot["geometry"]), 4)
        self.assertEqual(len(snapshot["frame_geometry"]), 4)

    def test_settings_dialog_action_buttons_use_improved_width(self):
        dialog = SettingsDialog(interval_seconds=30)

        self.assertGreaterEqual(dialog.ok_button.minimumWidth(), 110)
        self.assertGreaterEqual(dialog.cancel_button.minimumWidth(), 110)
        self.assertEqual(dialog.ok_button.objectName(), "primaryActionButton")
        self.assertEqual(dialog.cancel_button.objectName(), "secondaryActionButton")

    def test_settings_dialog_buttons_apply_blue_styles_directly(self):
        dialog = SettingsDialog(interval_seconds=30)

        self.assertIn("background: #2563eb;", dialog.ok_button.styleSheet())
        self.assertIn("color: white;", dialog.ok_button.styleSheet())
        self.assertIn("background: #3b82f6;", dialog.cancel_button.styleSheet())
        self.assertIn("color: white;", dialog.cancel_button.styleSheet())
        self.assertEqual(dialog.ok_button.text(), "保存")
        self.assertEqual(dialog.cancel_button.text(), "取消")
        self.assertEqual(dialog.ok_button.objectName(), "primaryActionButton")
        self.assertEqual(dialog.cancel_button.objectName(), "secondaryActionButton")

    def test_run_history_store_translates_auto_pause_reason(self):
        self.assertEqual(RunHistoryStore.translate_end_reason("auto_pause"), "自动暂停")


if __name__ == "__main__":
    unittest.main()
