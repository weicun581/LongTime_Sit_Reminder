import pathlib
import sys
import unittest

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from reminder_scheduler import ReminderScheduler


class ReminderSchedulerTest(unittest.TestCase):
    def test_start_pause_and_resume_use_remaining_seconds(self):
        scheduler = ReminderScheduler(interval_seconds=90, snooze_seconds=300)

        scheduler.start(now_ts=100)
        self.assertTrue(scheduler.is_running)
        self.assertEqual(scheduler.remaining_seconds, 90)
        self.assertEqual(scheduler.next_due_ts, 190)

        scheduler.pause(now_ts=130)
        self.assertTrue(scheduler.is_paused)
        self.assertFalse(scheduler.is_running)
        self.assertEqual(scheduler.remaining_seconds, 60)
        self.assertIsNone(scheduler.next_due_ts)

        scheduler.start(now_ts=200)
        self.assertFalse(scheduler.is_paused)
        self.assertTrue(scheduler.is_running)
        self.assertEqual(scheduler.remaining_seconds, 60)
        self.assertEqual(scheduler.next_due_ts, 260)

    def test_reset_uses_configured_duration_and_starts_immediately(self):
        scheduler = ReminderScheduler(interval_seconds=90, snooze_seconds=300)

        scheduler.start(now_ts=100)
        scheduler.pause(now_ts=130)
        scheduler.reset(now_ts=200)

        self.assertTrue(scheduler.is_running)
        self.assertFalse(scheduler.is_paused)
        self.assertEqual(scheduler.remaining_seconds, 90)
        self.assertEqual(scheduler.next_due_ts, 290)

    def test_update_interval_restarts_with_new_seconds(self):
        scheduler = ReminderScheduler(interval_seconds=90, snooze_seconds=300)

        scheduler.update_interval(interval_seconds=45, now_ts=100)

        self.assertEqual(scheduler.configured_duration_seconds, 45)
        self.assertEqual(scheduler.remaining_seconds, 45)
        self.assertTrue(scheduler.is_running)
        self.assertEqual(scheduler.next_due_ts, 145)


if __name__ == "__main__":
    unittest.main()
