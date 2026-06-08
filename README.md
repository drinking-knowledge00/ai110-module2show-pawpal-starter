# PawPal+ (Module 2 Project)

**PawPal+** is a smart pet care management system built with Python OOP and a Streamlit UI. It helps pet owners track daily routines — feedings, walks, medications, and appointments — while using algorithmic scheduling logic to organize, sort, and detect conflicts.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time, priority, frequency, due date)
- Produce a sorted daily plan with conflict warnings
- Automatically reschedule recurring tasks when they are marked complete

## Architecture

The system is built around four Python classes in [pawpal_system.py](pawpal_system.py):

| Class | Responsibility |
|-------|---------------|
| `Task` | Holds a single care activity — time, duration, priority, frequency, completion state |
| `Pet` | Stores pet info and owns a list of Tasks |
| `Owner` | Groups multiple Pets; provides flat access to all tasks |
| `Scheduler` | Sorts, filters, conflict-checks, and drives recurring task logic |

See [diagrams/uml.mmd](diagrams/uml.mmd) for the full Mermaid.js class diagram.

## Getting Started

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run the CLI demo:

```bash
python main.py
```

Launch the Streamlit app:

```bash
streamlit run app.py
```

## 🖥️ Sample Output

```
==================================================
  Today's Schedule
==================================================
  [○] 07:30 — Litter box cleaning (10 min) [priority: high] [freq: daily]
  [○] 08:00 — Morning walk (30 min) [priority: high] [freq: daily]
  [○] 08:00 — Heartworm medication (5 min) [priority: medium] [freq: monthly]
  [○] 09:00 — Breakfast feeding (10 min) [priority: high] [freq: daily]
  [○] 18:00 — Evening walk (30 min) [priority: high] [freq: daily]
  [○] 19:00 — Playtime (20 min) [priority: medium] [freq: daily]

==================================================
  Conflict Detection
==================================================
  ⚠ Conflict at 08:00: 'Heartworm medication' (for Biscuit) overlaps with 'Morning walk' (for Biscuit)

==================================================
  Biscuit's Tasks (Sorted)
==================================================
  [○] 08:00 — Morning walk (30 min) [priority: high] [freq: daily]
  [○] 08:00 — Heartworm medication (5 min) [priority: medium] [freq: monthly]
  [○] 09:00 — Breakfast feeding (10 min) [priority: high] [freq: daily]
  [○] 18:00 — Evening walk (30 min) [priority: high] [freq: daily]

==================================================
  Mark 'Morning walk' Complete → Check Recurrence
==================================================
  Recurring task created: Morning walk on 2026-06-09

==================================================
  Incomplete Tasks After Completion
==================================================
  [○] 07:30 — Litter box cleaning (10 min) [priority: high] [freq: daily]
  [○] 08:00 — Heartworm medication (5 min) [priority: medium] [freq: monthly]
  [○] 08:00 — Morning walk (30 min) [priority: high] [freq: daily]
  [○] 09:00 — Breakfast feeding (10 min) [priority: high] [freq: daily]
  [○] 18:00 — Evening walk (30 min) [priority: high] [freq: daily]
  [○] 19:00 — Playtime (20 min) [priority: medium] [freq: daily]
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting by time | `Scheduler.sort_by_time()` | Uses `sorted()` with a lambda on HH:MM string keys |
| Filter by pet | `Scheduler.filter_by_pet(pet_name)` | Case-insensitive match on `task.pet_name` |
| Filter by status | `Scheduler.filter_by_status(completed)` | Returns all completed or all incomplete tasks |
| Filter by priority | `Scheduler.filter_by_priority(priority)` | Returns tasks at a specific priority level |
| Conflict detection | `Scheduler.detect_conflicts()` | Returns warning strings for tasks sharing exact HH:MM time |
| Recurring tasks | `Task.mark_complete()` + `Scheduler.mark_task_complete()` | Daily tasks get `due_date + 1 day`; weekly get `+ 7 days`; new Task object added to pet automatically |
| Today's plan | `Scheduler.get_todays_schedule()` | Combines date filtering, status filtering, and sorting |

## 📸 Demo Walkthrough

1. **Set Owner** — Enter your name in the "Owner Setup" form. This creates an `Owner` instance stored in `st.session_state` so it persists across interactions.
2. **Add a Pet** — Use the "Add a Pet" form to register one or more pets (name, species, breed). Each becomes a `Pet` object attached to the owner.
3. **Schedule Tasks** — Use the "Schedule a Task" form to add care activities. Choose the pet, set a time (HH:MM), pick priority and frequency. The task is stored on the `Pet` object.
4. **View the Schedule** — The "Today's Schedule" section shows all tasks sorted chronologically. Use dropdowns to filter by pet or status (incomplete/completed).
5. **Conflict Warnings** — If two tasks share the same time, a yellow `st.warning` banner appears automatically, identifying the conflict by time and pet.
6. **Mark Tasks Done** — Click "Mark done" next to any task. Daily/weekly tasks are automatically rescheduled for the next occurrence (shown in a success message).
7. **Generate Plan** — Click "Generate Schedule" to see a clean `st.table` of today's sorted, incomplete tasks, along with any conflict warnings.

**CLI output**: run `python main.py` to see the same scheduling behaviors (sort, conflict detection, recurrence, filtering) directly in the terminal.

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest tests/ -v
```

The test suite covers:
- `Task.mark_complete()` — status change, recurrence for daily/weekly/once tasks
- `Pet.add_task()` / `remove_task()` — task count changes
- `Scheduler.sort_by_time()` — chronological ordering, empty list edge case
- `Scheduler.filter_by_pet()` — cross-pet isolation
- `Scheduler.filter_by_status()` — completed vs. incomplete split
- `Scheduler.detect_conflicts()` — same-time flagging, no false positives
- `Scheduler.mark_task_complete()` — recurrence insertion, one-time non-insertion
- `Scheduler.get_todays_schedule()` — date filtering, completion filtering

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.0.3, pluggy-1.6.0
collected 17 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED
tests/test_pawpal.py::test_mark_complete_once_returns_none PASSED
tests/test_pawpal.py::test_mark_complete_daily_returns_next_day PASSED
tests/test_pawpal.py::test_mark_complete_weekly_returns_next_week PASSED
tests/test_pawpal.py::test_add_task_increases_count PASSED
tests/test_pawpal.py::test_remove_task_decreases_count PASSED
tests/test_pawpal.py::test_remove_task_nonexistent_returns_false PASSED
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED
tests/test_pawpal.py::test_sort_empty_list_returns_empty PASSED
tests/test_pawpal.py::test_filter_by_pet_returns_only_matching_tasks PASSED
tests/test_pawpal.py::test_filter_by_status_incomplete PASSED
tests/test_pawpal.py::test_detect_conflicts_same_time PASSED
tests/test_pawpal.py::test_detect_conflicts_no_conflict PASSED
tests/test_pawpal.py::test_mark_task_complete_creates_recurring_task PASSED
tests/test_pawpal.py::test_mark_task_complete_once_does_not_create_new_task PASSED
tests/test_pawpal.py::test_get_todays_schedule_excludes_other_days PASSED
tests/test_pawpal.py::test_get_todays_schedule_excludes_completed PASSED

============================== 17 passed in 0.03s ==============================
```

**Confidence Level**: ⭐⭐⭐⭐ (4/5) — Core scheduling behaviors are fully covered. The main gap is integration-level tests for the Streamlit UI layer and persistence between sessions.
