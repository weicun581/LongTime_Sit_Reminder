from pathlib import Path

from PyQt5.QtWidgets import QTextBrowser

from run_history import RunHistoryStore


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


class RunHistoryDialog(QTextBrowser):
    def __init__(self, run_history_store, parent=None):
        super().__init__(parent)
        self.run_history_store = run_history_store
        self.setWindowTitle("运行记录")
        self.setReadOnly(True)
        self.setMinimumSize(640, 480)
        self.refresh()

    def refresh(self):
        total_seconds = self.run_history_store.total_seconds_for_day()
        lines = [f"今日累计：{RunHistoryStore.format_duration(total_seconds)}", "", "运行记录："]
        grouped_records = self.run_history_store.grouped_records_by_day()
        if not grouped_records:
            lines.append("暂无运行记录")
        else:
            for day, records in grouped_records.items():
                lines.append(day)
                for record in records:
                    lines.append(
                        "- "
                        f"{RunHistoryStore.format_time(record['start_at'])} -> {RunHistoryStore.format_time(record['end_at'])}"
                        f" | {RunHistoryStore.format_duration(record['duration_seconds'])}"
                        f" | {RunHistoryStore.translate_end_reason(record['end_reason'])}"
                    )
        self.setPlainText("\n".join(lines))

    @staticmethod
    def _format_duration(total_seconds):
        return RunHistoryStore.format_duration(total_seconds)

    @staticmethod
    def _format_time(ts):
        return RunHistoryStore.format_time(ts)

    @staticmethod
    def _translate_end_reason(end_reason):
        return RunHistoryStore.translate_end_reason(end_reason)
