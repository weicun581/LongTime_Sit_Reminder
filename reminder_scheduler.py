class ReminderScheduler:
    def __init__(self, interval_seconds, snooze_seconds):
        self.configured_duration_seconds = interval_seconds
        self.snooze_seconds = snooze_seconds
        self.remaining_seconds = interval_seconds
        self.is_running = False
        self.is_paused = False
        self.is_snoozed = False
        self.next_due_ts = None

    def start(self, now_ts):
        if self.is_running:
            return
        self.is_running = True
        self.is_paused = False
        self.next_due_ts = now_ts + self.remaining_seconds

    def pause(self, now_ts):
        if not self.is_running or self.next_due_ts is None:
            return
        self.remaining_seconds = max(0, self.next_due_ts - now_ts)
        self.next_due_ts = None
        self.is_running = False
        self.is_paused = True

    def reset(self, now_ts):
        self.remaining_seconds = self.configured_duration_seconds
        self.is_snoozed = False
        self.is_running = False
        self.start(now_ts)

    def snooze(self, now_ts):
        self.remaining_seconds = self.snooze_seconds
        self.is_snoozed = True
        self.is_running = False
        self.start(now_ts)

    def complete_reminder(self, now_ts):
        self.remaining_seconds = self.configured_duration_seconds
        self.is_snoozed = False
        self.is_running = False
        self.start(now_ts)

    def update_interval(self, interval_seconds, now_ts):
        self.configured_duration_seconds = interval_seconds
        self.remaining_seconds = interval_seconds
        self.is_snoozed = False
        self.is_running = False
        self.start(now_ts)
