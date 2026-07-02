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

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

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

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->


## 📸 Sample Output

=== Today's Schedule - 2026-07-02 (Alex Morgan) ===
  07:00-07:30  Morning Walk                 [Biscuit]  (priority: high)
  08:00-08:10  Breakfast Feeding            [Mochi]  (priority: medium)
  14:30-14:35  Afternoon Medication         [Biscuit]  (priority: high)
  19:00-19:20  Evening Play / Enrichment    [Mochi]  (priority: low)

  4 task(s) scheduled.