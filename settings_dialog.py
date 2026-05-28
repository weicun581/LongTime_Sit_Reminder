from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLabel, QLineEdit, QVBoxLayout


class SettingsDialog(QDialog):
    def __init__(self, interval_seconds, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置提醒间隔")
        self._interval_seconds = interval_seconds
        self.setMinimumWidth(360)
        self.setStyleSheet(
            """
            QDialog {
                background: #ffffff;
            }
            QLabel {
                color: #374151;
            }
            #settingsHoursInput,
            #settingsMinutesInput,
            #settingsSecondsInput {
                min-height: 36px;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 0 12px;
                font-size: 14px;
                background: #ffffff;
            }
            #settingsErrorLabel {
                color: #dc2626;
                font-size: 13px;
            }
            QPushButton {
                min-height: 38px;
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
                background: #3b82f6;
                color: white;
                border: none;
            }
            #secondaryActionButton:hover {
                background: #2563eb;
            }
            """
        )

        hours, remainder = divmod(interval_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        self.hours_input = QLineEdit(str(hours), self)
        self.hours_input.setPlaceholderText("小时")
        self.hours_input.setObjectName("settingsHoursInput")
        self.hours_input.setAlignment(Qt.AlignLeft)

        self.minutes_input = QLineEdit(str(minutes), self)
        self.minutes_input.setPlaceholderText("分钟")
        self.minutes_input.setObjectName("settingsMinutesInput")
        self.minutes_input.setAlignment(Qt.AlignLeft)

        self.seconds_input = QLineEdit(str(seconds), self)
        self.seconds_input.setPlaceholderText("秒")
        self.seconds_input.setObjectName("settingsSecondsInput")
        self.seconds_input.setAlignment(Qt.AlignLeft)

        self.error_label = QLabel("", self)
        self.error_label.setObjectName("settingsErrorLabel")
        self.error_label.setAlignment(Qt.AlignLeft)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.ok_button = self.button_box.button(QDialogButtonBox.Ok)
        self.cancel_button = self.button_box.button(QDialogButtonBox.Cancel)
        self.ok_button.setObjectName("primaryActionButton")
        self.cancel_button.setObjectName("secondaryActionButton")
        self.ok_button.setStyleSheet(
            "background: #2563eb; color: white; border: none;"
        )
        self.cancel_button.setStyleSheet(
            "background: #3b82f6; color: white; border: none;"
        )
        self.ok_button.setText("保存")
        self.cancel_button.setText("取消")
        self.ok_button.setMinimumWidth(110)
        self.cancel_button.setMinimumWidth(110)
        self.button_box.accepted.connect(self.try_accept)
        self.button_box.rejected.connect(self.reject)

        form_layout = QFormLayout()
        form_layout.addRow("小时", self.hours_input)
        form_layout.addRow("分钟", self.minutes_input)
        form_layout.addRow("秒", self.seconds_input)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        layout.addLayout(form_layout)
        layout.addWidget(self.error_label)
        layout.addWidget(self.button_box)

    def try_accept(self):
        try:
            hours = int(self.hours_input.text())
            minutes = int(self.minutes_input.text())
            seconds = int(self.seconds_input.text())
        except ValueError:
            self.error_label.setText("请输入非负整数")
            return False

        if hours < 0 or minutes < 0 or seconds < 0:
            self.error_label.setText("请输入非负整数")
            return False

        if minutes > 59 or seconds > 59:
            self.error_label.setText("分钟和秒必须在 0 到 59 之间")
            return False

        interval_seconds = hours * 3600 + minutes * 60 + seconds
        if interval_seconds <= 0:
            self.error_label.setText("请输入大于 0 的提醒时长")
            return False

        self._interval_seconds = interval_seconds
        self.error_label.setText("")
        self.accept()
        return True

    def get_interval_seconds(self):
        return self._interval_seconds
