# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- Run the app: `python main.py`
- Run all tests: `python -m unittest discover -s tests`
- Run a single test module: `python -m unittest tests.test_app_controller`
- Run a single test case: `python -m unittest tests.test_scheduler.ReminderSchedulerTest.test_update_interval_resets_schedule_immediately`

## Architecture overview

This repository is a small PyQt5 desktop reminder app built around a thin bootstrap layer, one orchestration controller, and a few focused UI/state modules.

- `main.py` creates `QApplication`, resolves the repo root as `base_dir`, and hands control to `AppController`.
- `app_controller.py` is the central coordinator. It loads `config.json`, creates the scheduler, owns the tray icon and preview window, starts a 1-second `QTimer`, opens dialogs, and translates dialog actions into scheduler state transitions.
- `reminder_scheduler.py` is the timing/state model. It is intentionally UI-free and tracks countdown state through `remaining_seconds`, `next_due_ts`, and flags such as paused/snoozed/running.
- `config.py` persists only the reminder interval. The current stored format is `interval_seconds`; loading still accepts legacy `interval_minutes` and converts it.
- `settings_dialog.py` edits the interval as hours/minutes/seconds and validates all user input before the controller saves the new config and restarts the schedule.
- `reminder_dialog.py` is the due-now modal. It returns either `complete` or `snooze`, and `AppController._handle_dialog_finished()` maps that result back into scheduler actions.
- `tray_icon.py` defines the system tray menu surface only; business logic stays in `AppController` via connected actions.

## Data and control flow

Normal runtime flow:

1. `AppController.start()` verifies tray support, shows the tray icon and preview window, starts the scheduler, and starts the 1-second polling timer.
2. Each timer tick calls `AppController._check_due()`, which first refreshes the preview countdown and then decides whether the reminder dialog should open.
3. When the reminder dialog closes, the selected action updates the scheduler (`snooze()` or `complete_reminder()`), then the preview countdown is refreshed.
4. When settings are saved, the controller writes `config.json`, calls `scheduler.update_interval(...)`, and immediately refreshes the displayed countdown.

## Testing notes

- Tests use `unittest`, not `pytest`.
- UI-heavy tests instantiate a real `QApplication` and exercise widgets/controllers directly.
- `tests/test_app_controller.py` is the highest-value integration-style test file because it covers interactions between config, scheduler state, tray actions, preview UI, and reminder dialogs.
- `tests/test_scheduler.py` and `tests/test_reminder_scheduler.py` both cover scheduler behavior; if scheduler behavior changes, update both files consistently.

## Repo-specific notes

- There is currently no `requirements.txt`, `pyproject.toml`, or `README.md`, so dependency/setup instructions should be inferred cautiously and only from verified code usage.
- The repository currently includes generated/runtime artifacts and scratch files in the root (for example `__pycache__/` and `*_stdout.log` / `*_stderr.log` files). Avoid committing additional temporary files unless the user explicitly asks for them.
