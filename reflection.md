# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

I designed four classes, each with a single clear responsibility:

- **Task** — a dataclass representing one care activity. It owns its own recurrence logic (`mark_complete` returns the next Task when frequency is daily or weekly), which keeps the Scheduler thin.
- **Pet** — a dataclass holding pet metadata and a list of Tasks. It exposes `add_task`, `remove_task`, and `get_tasks` so other classes never touch `pet.tasks` directly.
- **Owner** — a plain class that aggregates multiple Pets. Its `get_all_tasks()` method flattens all pet task lists into one, giving the Scheduler a single entry point to all data.
- **Scheduler** — the algorithmic brain. It holds a reference to the Owner and provides sorting (`sort_by_time`), filtering (`filter_by_pet`, `filter_by_status`, `filter_by_priority`), conflict detection (`detect_conflicts`), and schedule generation (`get_todays_schedule`).

Three core user actions I identified: (1) add a pet, (2) schedule a task with a time and frequency, (3) view today's tasks sorted by time with conflict warnings shown.

**b. Design changes**

Originally I considered putting recurrence logic inside the Scheduler, but I moved it into `Task.mark_complete()` instead. The reasoning: a Task knows its own frequency and due date, so it should generate its own successor. The Scheduler's `mark_task_complete` method simply calls `task.mark_complete()` and, if a next Task is returned, appends it to the pet — a clean separation of concerns. I also added `filter_by_priority` late in implementation because the UI filtering felt incomplete without it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers:
- **Time** (HH:MM string) — primary sort key for ordering the day
- **Due date** — `get_todays_schedule` only includes tasks whose `due_date` equals today
- **Completion status** — completed tasks are excluded from the daily plan
- **Frequency** — determines whether a new task is generated on completion

Priority was used as a filter and display label rather than a scheduling constraint, because the instructions focused on time-based ordering rather than priority-based slot allocation.

**b. Tradeoffs**

The conflict detector checks for *exact* HH:MM string matches only. It does not check whether a 30-minute task starting at 08:00 overlaps with a 15-minute task starting at 08:20. This is a deliberate simplification: exact-match detection is O(n) with a dictionary, it is predictable, and for a single-owner daily planner the granularity is sufficient. A full overlap check would require computing end times and interval intersection, which adds complexity without much practical benefit for a home pet care scenario where tasks rarely need minute-perfect precision.

---

## 3. AI Collaboration

**a. How you used AI**

I used the AI coding assistant for three things: (1) brainstorming the four-class architecture and verifying the relationships made sense before writing code, (2) generating the Mermaid.js UML diagram from my verbal description, and (3) helping draft docstrings once the implementation was stable. The most effective prompts were narrow and attached a specific file: "Given this Pet class, how should Scheduler retrieve all tasks from the Owner's pets?" beats "help me design a scheduler."

**b. Judgment and verification**

An early AI suggestion put `sort_by_time` and `filter_by_pet` directly on the `Owner` class rather than on a separate `Scheduler`. I rejected this because mixing algorithmic logic into the data model violates single-responsibility — Owner should manage *what pets it holds*, not *how tasks are queried*. I verified the decision was correct when writing tests: having Scheduler as a separate class let me inject any Owner and test scheduling behavior in isolation without touching the data model.

---

## 4. Testing and Verification

**a. What you tested**

17 tests across four behavioral categories:
- **Task completion and recurrence** — verifies that `mark_complete` changes status and generates the correct next Task for daily, weekly, and one-time frequencies.
- **Pet task list management** — verifies that `add_task` increases count and `remove_task` decreases it (or returns False for missing titles).
- **Sorting correctness** — verifies that tasks added in random time order come out in chronological order; also tests the empty-list edge case.
- **Filtering and conflict detection** — verifies per-pet isolation, completed/incomplete split, same-time conflict flagging, and the absence of false positives.
- **Schedule generation** — verifies that `get_todays_schedule` excludes tasks due on other days and excludes already-completed tasks.

These tests matter because the scheduling behaviors are the core value of the app — if sorting or recurrence breaks silently, the UI will display wrong information with no error raised.

**b. Confidence**

⭐⭐⭐⭐ (4/5). All 17 tests pass and cover the happy path and most edge cases. Gaps I would close next: (1) overlap-based conflict detection beyond exact-time matching, (2) behavior when the Owner has zero pets, (3) Streamlit session state persistence across page refreshes (requires a browser-level integration test).

---

## 5. Reflection

**a. What went well**

The CLI-first workflow was the most effective decision I made. Building `pawpal_system.py` and verifying it with `main.py` before touching the Streamlit UI meant the backend was solid when I connected it. Every UI section just called methods I had already tested — no debugging of logic through a browser.

**b. What you would improve**

I would add JSON persistence so that pets and tasks survive a page reload. Right now all state lives in `st.session_state`, which resets if the browser tab is closed. Adding `save_to_json` / `load_from_json` methods to `Owner` would solve this cleanly without changing the class interfaces.

**c. Key takeaway**

Being the "lead architect" means making the structural decisions the AI will not make for you: where does recurrence logic live, should the scheduler be separate from the data model, which behaviors need tests first? AI is excellent at filling in implementation details once the architecture is decided, but it defaults to "put everything in one class" unless you push back. The human's job is to hold the design intent and evaluate every suggestion against it.
