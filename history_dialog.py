from pathlib import Path

from PyQt5.QtWidgets import QTextBrowser


class HistoryDialog(QTextBrowser):
    def __init__(self, markdown_path, parent=None):
        super().__init__(parent)
        self.markdown_path = Path(markdown_path)
        self.setWindowTitle("历史版本")
        self.setReadOnly(True)
        self.setMinimumSize(640, 480)
        self._load_content()

    def _load_content(self):
        if self.markdown_path.exists():
            self.setMarkdown(self.markdown_path.read_text(encoding="utf-8"))
        else:
            self.setPlainText("暂无历史版本记录")
