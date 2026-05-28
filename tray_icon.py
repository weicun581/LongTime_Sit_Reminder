from PyQt5.QtWidgets import QAction, QMenu, QSystemTrayIcon


class TrayIcon(QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        super().__init__(icon, parent)
        self._show_main_page_action = QAction("显示主页面", self)
        self._settings_action = QAction("设置", self)
        self._exit_action = QAction("退出", self)

        menu = QMenu(parent)
        menu.addAction(self._show_main_page_action)
        menu.addAction(self._settings_action)
        menu.addSeparator()
        menu.addAction(self._exit_action)

        self.setContextMenu(menu)

    @property
    def show_main_page_action(self):
        return self._show_main_page_action

    @property
    def settings_action(self):
        return self._settings_action

    @property
    def exit_action(self):
        return self._exit_action
