from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QLabel, QPushButton, QVBoxLayout


class ReminderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("久坐提醒")
        self.setModal(True)
        self._action = None
        self.setMinimumWidth(360)
        self.setStyleSheet(
            """
            QDialog {
                background: #ffffff;
            }
            QLabel {
                color: #4b5563;
            }
            #reminderStatusLabel {
                font-size: 22px;
                font-weight: 700;
                color: #d97706;
            }
            #reminderMessageLabel {
                font-size: 14px;
                color: #374151;
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
                background: white;
                color: #374151;
                border: 1px solid #cbd5e1;
            }
            #secondaryActionButton:hover {
                background: #f8fafc;
            }
            """
        )

        self.status_label = QLabel("现在该起来活动了", self)
        self.status_label.setObjectName("reminderStatusLabel")

        self.message_label = QLabel("你已经坐了很久，起来活动一下吧。", self)
        self.message_label.setObjectName("reminderMessageLabel")
        self.message_label.setWordWrap(True)

        self.button_box = QDialogButtonBox(self)
        self.close_button = QPushButton("关闭", self)
        self.close_button.setObjectName("secondaryActionButton")
        self.snooze_button = QPushButton("稍后提醒", self)
        self.snooze_button.setObjectName("primaryActionButton")
        self.button_box.addButton(self.close_button, QDialogButtonBox.AcceptRole)
        self.button_box.addButton(self.snooze_button, QDialogButtonBox.ActionRole)

        self.close_button.clicked.connect(self._handle_close)
        self.snooze_button.clicked.connect(self._handle_snooze)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        layout.addWidget(self.status_label)
        layout.addWidget(self.message_label)
        layout.addWidget(self.button_box)

    def _handle_close(self):
        self._action = "complete"
        self.accept()

    def _handle_snooze(self):
        self._action = "snooze"
        self.accept()

    def get_action(self):
        return self._action
