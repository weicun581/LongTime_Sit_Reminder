import json
from collections import OrderedDict
from datetime import datetime
from pathlib import Path


class RunHistoryStore:
    def __init__(self, history_path=None):
        self.history_path = Path(history_path) if history_path is not None else None
        self.records = self._load_records()

    def _load_records(self):
        if self.history_path is None or not self.history_path.exists():
            return []
        data = json.loads(self.history_path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []

    def _save_records(self):
        if self.history_path is None:
            return
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        self.history_path.write_text(
            json.dumps(self.records, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add_record(self, start_at, end_at, end_reason):
        duration_seconds = max(0, int(end_at) - int(start_at))
        record = {
            "start_at": int(start_at),
            "end_at": int(end_at),
            "duration_seconds": duration_seconds,
            "end_reason": end_reason,
        }
        self.records.append(record)
        self._save_records()
        return record

    def total_seconds_for_day(self, day_ts=None):
        if day_ts is None:
            if not self.records:
                return 0
            day = datetime.fromtimestamp(self.records[-1]["start_at"]).date()
        else:
            day = datetime.fromtimestamp(day_ts).date()
        return sum(
            record["duration_seconds"]
            for record in self.records
            if datetime.fromtimestamp(record["start_at"]).date() == day
        )

    def grouped_records_by_day(self):
        grouped = OrderedDict()
        for record in self.records:
            day_key = datetime.fromtimestamp(record["start_at"]).strftime("%Y-%m-%d")
            grouped.setdefault(day_key, []).append(record)
        return grouped

    @staticmethod
    def format_duration(total_seconds):
        total_seconds = max(0, int(total_seconds))
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @staticmethod
    def format_time(ts):
        return datetime.fromtimestamp(int(ts)).strftime("%H:%M:%S")

    @staticmethod
    def format_day(ts):
        return datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d")

    @staticmethod
    def translate_end_reason(end_reason):
        labels = {
            "pause": "暂停",
            "reset": "重置",
            "complete": "完成",
            "snooze": "稍后提醒",
            "auto_pause": "自动暂停",
        }
        return labels.get(end_reason, end_reason)


class RunHistoryDialog:
    @staticmethod
    def format_duration(total_seconds):
        return RunHistoryStore.format_duration(total_seconds)

    @staticmethod
    def format_time(ts):
        return RunHistoryStore.format_time(ts)

    @staticmethod
    def translate_end_reason(end_reason):
        return RunHistoryStore.translate_end_reason(end_reason)
