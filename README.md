# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## ✨ Features

Implemented algorithms and behaviors (see the `Scheduler` and `Task` classes in
[`pawpal_system.py`](pawpal_system.py)):

- **Sorting by time** — tasks are ordered chronologically by their
  `earliest_start`, with timeless tasks pushed to the end
  (`Scheduler.sort_by_time()`).
- **Filtering** — narrow tasks by completion status, by pet name
  (case-insensitive), or both combined (`Scheduler.filter_tasks()`).
- **Conflict detection** — finds overlapping tasks within a single pet and
  across different pets, ignoring windows that merely touch
  (`Scheduler.detect_conflicts()` / `Task.conflicts_with()`).
- **Conflict warnings** — a lightweight, non-crashing warning message
  (empty when clear) instead of raising an exception
  (`Scheduler.conflict_warning()`).
- **Conflict resolution** — overlapping tasks are automatically spread later
  so the generated day plan never collides (`Scheduler.resolve_conflicts()`,
  applied by `generate_plan()`).
- **Daily & weekly recurrence** — completing a recurring task auto-creates the
  next occurrence (daily = +1 day, weekly = +7 days, computed with
  `timedelta`) (`Task.spawn_next()` via `Scheduler.complete_task()`).
- **Daily plan generation** — aggregates every task across all of an owner's
  pets and anchors each to its earliest start
  (`Scheduler.load_tasks_from_owner()` + `get_plan_for_day()`).
- **Completion tracking** — mark tasks done and query status
  (`Task.mark_completed()` / `Task.is_completed()`).
- **Multi-pet management** — add, select, and remove pets, each with its own
  task list (`Owner.add_pet()` / `remove_pet()`, `Pet.add_task()`).

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

Optionally, run with coverage:

```bash
python -m pytest --cov
```

**What the tests cover** (`tests/test_pawpal.py`, 9 tests):

- **Task completion** — `mark_completed()` flips a task's status to done.
- **Adding tasks** — `Pet.add_task()` increases the pet's task count.
- **Recurrence** — completing a daily task spawns the next-day occurrence;
  a non-recurring task spawns nothing.
- **Sorting** — `Scheduler.sort_by_time()` returns tasks in chronological order.
- **Conflict detection** — overlaps within one pet and across different pets,
  duplicate (identical) start times, and the no-conflict "touching windows" edge case.
- **Lightweight conflict warning** — `conflict_warning()` returns a message
  (never raises) and an empty string when there are no conflicts.

Terminal output of a successful run:

```
$ python -m pytest
============================= test session starts =============================
platform win32 -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Claude_dev\ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collected 9 items

tests\test_pawpal.py .........                                           [100%]

============================== 9 passed in 0.03s ==============================
```

### Confidence Level: ⭐⭐⭐⭐☆ (4 / 5)

All 9 tests pass and cover the core scheduling logic — sorting, filtering,
recurrence, and conflict detection — including edge cases like touching time
windows and non-recurring tasks. Confidence is high but not maxed out because a
few areas are still untested or unimplemented: owner availability
(`find_free_slot`), serialization (`to_dict`/`from_dict`), overdue detection
(`is_overdue`), and recurrence frequencies beyond daily/weekly. Adding tests
for those would move this to 5 stars.

## 📐 Smarter Scheduling

All scheduling logic lives in the `Scheduler` and `Task` classes in
[`pawpal_system.py`](pawpal_system.py). Each feature below names the method
that implements it.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Orders tasks by their `earliest_start`; timeless tasks sort last. `prioritize()` delegates to it. |
| Filtering | `Scheduler.filter_tasks(completed=..., pet_name=...)` | Filter by completion status, by pet name (case-insensitive), or both combined. |
| Conflict detection | `Scheduler.detect_conflicts()`, `has_conflicts()`, `conflict_warning()`, `Task.conflicts_with()` | Finds overlapping tasks (same pet or across pets); returns a lightweight warning instead of raising. |
| Conflict resolution | `Scheduler.resolve_conflicts()` (used by `generate_plan()`) | Spreads overlapping slots later so the generated plan never collides. |
| Recurring tasks | `Task.next_occurrence()`, `Task.spawn_next()`, `Scheduler.complete_task()` | Completing a `daily`/`weekly` task auto-creates the next occurrence. |

### Sorting behavior — `Scheduler.sort_by_time()`
Returns the scheduler's tasks ordered by their `earliest_start` time attribute
using a sort key. Tasks without a time sort to the end. `prioritize()` is a
thin alias so callers have a single source of truth. Used by the app's
"Task list" so tasks always display in chronological order regardless of
insertion order.

### Filtering behavior — `Scheduler.filter_tasks(completed=None, pet_name=None)`
- `completed=True` keeps only done tasks, `False` only pending, `None` keeps any.
- `pet_name` restricts to the owner's pet(s) with that name (case-insensitive).
- Both filters combine (e.g. *pending tasks for "Mochi"*).

Completion status is tracked by `Task.last_completed` and read via
`Task.is_completed()`; `Task.mark_completed(timestamp)` records completion.

### Conflict detection logic — `Scheduler.detect_conflicts()`
Compares each task's `[earliest_start, earliest_start + duration)` window
against every other task (`Task.conflicts_with()`), catching clashes **within
one pet and across different pets**. Windows that merely touch (one ends as
the next begins) do not count as a conflict.

- `has_conflicts() -> bool` — quick boolean check.
- `conflict_warning() -> str` — **lightweight, non-raising** strategy that
  returns a human-readable warning (empty string when clear), so callers can
  `if msg: warn(msg)` and keep running instead of crashing.
- Detected conflicts are surfaced in `app.py` before scheduling, then
  automatically spread apart by `resolve_conflicts()` when the plan is built.

### Recurring task logic — `Task.spawn_next()` / `Scheduler.complete_task()`
When a `daily` or `weekly` task is marked complete via
`Scheduler.complete_task(task, timestamp)`, a fresh, uncompleted instance is
auto-created for the next occurrence and attached to the owning pet:

- **daily** → next due date is completion date **+ 1 day**
- **weekly** → completion date **+ 7 days**

Dates are computed with Python's `timedelta`, so month/year rollovers and leap
years are handled accurately. Recurrence type is stored on `Task.recurrence`
(a `Recurrence` with `freq`); non-recurring tasks spawn nothing.

## 🎬 Demo Walkthrough

### Main UI features

Launch the app with `streamlit run app.py`. The single-page UI lets a user:

- **Owner** — set the owner's name.
- **Pets** — add a pet (name + species), pick the *active pet* from a dropdown,
  or remove the selected pet. The owner can hold multiple pets, each with its
  own task list.
- **Tasks** — add a care task for the active pet with a title, duration,
  priority, earliest start time, and an optional **Repeats** setting
  (none / daily / weekly). Clear the active pet's tasks with one button.
- **Task list** — a filterable, time-sorted table with a **Show**
  (All / Pending / Completed) filter and a **Pet** filter. Each row has a
  checkbox to mark the task complete (recurring tasks show a 🔁 tag).
- **Build Schedule** — a live conflict banner plus a **Generate schedule**
  button that produces the day's plan as a clean table.

### Example workflow

1. Enter the owner's name (e.g. *Jordan*).
2. Add a pet — type "Biscuit", pick *dog*, click **Add pet**. Select it as the
   active pet.
3. Add tasks for Biscuit: "Morning Walk" at 07:00 (30 min, high), and an
   "Evening Feed" at 18:00 set to **daily**.
4. Watch them appear in the **Task list**, automatically sorted by time.
5. Tick "Morning Walk" complete — it greys out; a recurring task would spawn
   its next occurrence automatically.
6. Add a second task at 07:00 to trigger the **conflict warning** banner.
7. Click **Generate schedule** to see today's non-overlapping plan.

### Key Scheduler behaviors shown

- **Sorting by time** — the task list and schedule are always chronological,
  regardless of the order tasks were added (`Scheduler.sort_by_time()`).
- **Filtering** — the Show/Pet filters call `Scheduler.filter_tasks()`.
- **Conflict warnings** — same-time tasks (within a pet or across pets) raise a
  non-blocking warning (`Scheduler.conflict_warning()`), then are spread apart
  in the generated plan (`resolve_conflicts()`).
- **Daily recurrence** — completing a daily/weekly task auto-creates the next
  occurrence (`Scheduler.complete_task()` → `Task.spawn_next()`).

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

### Sample CLI output (`python main.py`)

The `main.py` script exercises the same logic in the terminal — adding tasks
out of order, sorting, filtering, spawning a recurring task, flagging a
conflict, and printing today's schedule:

```
=== Tasks in INSERTION order (as added) ===
  07:00  Morning Walk                 [done   ] (priority: high)
  14:30  Afternoon Medication         [pending] (priority: high)
  19:00  Evening Play / Enrichment    [pending] (priority: low)
  08:00  Breakfast Feeding            [pending] (priority: medium)
  07:00  Morning Medication           [pending] (priority: high)

=== Tasks sorted by time (Scheduler.sort_by_time) ===
  07:00  Morning Walk                 [done   ] (priority: high)
  07:00  Morning Medication           [pending] (priority: high)
  08:00  Breakfast Feeding            [pending] (priority: medium)
  14:30  Afternoon Medication         [pending] (priority: high)
  19:00  Evening Play / Enrichment    [pending] (priority: low)

=== Filtering (Scheduler.filter_tasks) ===
  pending only   (4): ['Afternoon Medication', 'Evening Play / Enrichment', 'Breakfast Feeding', 'Morning Medication']
  completed only (1): ['Morning Walk']
  Mochi's tasks  (3): ['Evening Play / Enrichment', 'Breakfast Feeding', 'Morning Medication']

=== Recurrence: completing a task spawns the next occurrence ===
  before complete: ['daily_walk']
  completed 'daily_walk' -> spawned 'daily_walk#2026-07-03' (pending, starts 07:00)
  after complete : ['daily_walk', 'daily_walk#2026-07-03']

=== Conflict check (Scheduler.conflict_warning) ===
  Warning: 1 scheduling conflict(s) detected:
    - Morning Walk (07:00) overlaps Morning Medication (07:00) [different pets]
  (program continues normally after the warning)

=== Today's Schedule - 2026-07-02 (Alex Morgan) ===
  07:00-07:30  Morning Walk                 [Biscuit]  (priority: high)
  07:30-07:35  Morning Medication           [Mochi]  (priority: high)
  08:00-08:10  Breakfast Feeding            [Mochi]  (priority: medium)
  14:30-14:35  Afternoon Medication         [Biscuit]  (priority: high)
  19:00-19:20  Evening Play / Enrichment    [Mochi]  (priority: low)

  5 task(s) scheduled.
```