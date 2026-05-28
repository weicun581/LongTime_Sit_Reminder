import pathlib
import sys
import unittest

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from reminder_scheduler import ReminderScheduler


class ReminderSchedulerTest(unittest.TestCase):
    def test_start_sets_due_time_from_interval_seconds(self):
        scheduler = ReminderScheduler(interval_seconds=3600, snooze_seconds=300)

        scheduler.start(now_ts=1000)

        self.assertEqual(scheduler.next_due_ts, 1000 + 3600)
        self.assertFalse(scheduler.is_snoozed)

    def test_snooze_pushes_due_time_by_snooze_seconds(self):
        scheduler = ReminderScheduler(interval_seconds=3600, snooze_seconds=300)
        scheduler.start(now_ts=1000)

        scheduler.snooze(now_ts=1100)

        self.assertEqual(scheduler.next_due_ts, 1100 + 300)
        self.assertTrue(scheduler.is_snoozed)

    def test_complete_reminder_starts_next_full_interval(self):
        scheduler = ReminderScheduler(interval_seconds=3600, snooze_seconds=300)
        scheduler.start(now_ts=1000)
        scheduler.snooze(now_ts=1100)

        scheduler.complete_reminder(now_ts=1200)

        self.assertEqual(scheduler.next_due_ts, 1200 + 3600)
        self.assertFalse(scheduler.is_snoozed)

    def test_update_interval_resets_schedule_immediately(self):
        scheduler = ReminderScheduler(interval_seconds=3600, snooze_seconds=300)
        scheduler.start(now_ts=1000)

        scheduler.update_interval(interval_seconds=1800, now_ts=1300)

        self.assertEqual(scheduler.configured_duration_seconds, 1800)
        self.assertEqual(scheduler.next_due_ts, 1300 + 1800)
        self.assertFalse(scheduler.is_snoozed)


if __name__ == "__main__":
    unittest.main()
