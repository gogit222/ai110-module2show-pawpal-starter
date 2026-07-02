"""Simple tests for the PawPal+ domain model.

Run from the project root with:
    python -m pytest tests/
or, without pytest installed:
    python tests/test_pawpal.py
"""

import os
import sys
from datetime import datetime, time

# Allow running this file directly (adds the project root to the import path).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pawpal_system import (  # noqa: E402
    Owner,
    Pet,
    Task,
    Scheduler,
    Recurrence,
    Priority,
)


def make_task(task_id="task_001", name="Morning Walk"):
    return Task(
        task_id=task_id,
        name=name,
        duration_minutes=30,
        priority=Priority.HIGH,
        earliest_start=time(7, 0),
        assigned_pet_id="pet_001",
    )


def test_task_completion_changes_status():
    """Calling mark_completed() flips the task from not-done to done."""
    task = make_task()

    # Before: no completion timestamp -> status is "not completed".
    assert task.last_completed is None
    assert task.is_completed() is False

    completed_at = datetime(2026, 7, 2, 7, 30)
    task.mark_completed(completed_at)

    # After: status has changed to "completed".
    assert task.last_completed == completed_at
    assert task.is_completed() is True


def test_adding_task_increases_pet_task_count():
    """Adding a task to a Pet increases that pet's task count by one."""
    pet = Pet(pet_id="pet_001", name="Biscuit", species="dog")

    assert len(pet.get_tasks()) == 0

    pet.add_task(make_task())

    assert len(pet.get_tasks()) == 1

    pet.add_task(make_task(task_id="task_002", name="Evening Walk"))

    assert len(pet.get_tasks()) == 2


def test_completing_recurring_task_spawns_next_occurrence():
    """Completing a daily task auto-creates the next-day occurrence."""
    owner = Owner(owner_id="owner_001", name="Alex")
    pet = Pet(pet_id="pet_001", name="Biscuit", species="dog")
    walk = Task(
        task_id="walk",
        name="Walk",
        duration_minutes=30,
        earliest_start=time(7, 0),
        recurrence=Recurrence(freq="daily"),
        assigned_pet_id="pet_001",
    )
    pet.add_task(walk)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    scheduler.load_tasks_from_owner()
    assert len(pet.get_tasks()) == 1

    upcoming = scheduler.complete_task(walk, datetime(2026, 7, 2, 7, 35))

    # The original is now complete, and a fresh next-day instance exists.
    assert walk.is_completed() is True
    assert upcoming is not None
    assert upcoming.is_completed() is False
    assert upcoming.task_id == "walk#2026-07-03"
    assert len(pet.get_tasks()) == 2


def test_completing_non_recurring_task_spawns_nothing():
    """Completing a one-off task returns None and adds no new task."""
    owner = Owner(owner_id="owner_001", name="Alex")
    pet = Pet(pet_id="pet_001", name="Biscuit", species="dog")
    pet.add_task(make_task())
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    scheduler.load_tasks_from_owner()

    upcoming = scheduler.complete_task(pet.get_tasks()[0], datetime(2026, 7, 2, 7, 35))

    assert upcoming is None
    assert len(pet.get_tasks()) == 1


def test_detect_conflicts_same_and_different_pets():
    """detect_conflicts finds overlaps within a pet and across pets."""
    owner = Owner(owner_id="owner_001", name="Alex")
    mochi = Pet(pet_id="pet_001", name="Mochi", species="cat")
    biscuit = Pet(pet_id="pet_002", name="Biscuit", species="dog")
    # Mochi has two overlapping tasks (same pet).
    mochi.add_task(
        Task(task_id="m1", name="Walk", duration_minutes=30,
             earliest_start=time(7, 0), assigned_pet_id="pet_001")
    )
    mochi.add_task(
        Task(task_id="m2", name="Feed", duration_minutes=10,
             earliest_start=time(7, 15), assigned_pet_id="pet_001")
    )
    # Biscuit overlaps Mochi's walk (different pets).
    biscuit.add_task(
        Task(task_id="b1", name="Meds", duration_minutes=15,
             earliest_start=time(7, 10), assigned_pet_id="pet_002")
    )
    owner.add_pet(mochi)
    owner.add_pet(biscuit)

    scheduler = Scheduler(owner=owner)
    scheduler.load_tasks_from_owner()

    conflicts = scheduler.detect_conflicts()
    assert scheduler.has_conflicts() is True
    # m1/m2 (same pet), m1/b1 and m2/b1 (cross pet) => 3 conflicting pairs.
    assert len(conflicts) == 3
    assert any(c.same_pet for c in conflicts)
    assert any(not c.same_pet for c in conflicts)


def test_no_conflict_for_touching_windows():
    """Tasks that merely touch (one ends as the next starts) do not conflict."""
    a = Task(task_id="a", name="Walk", duration_minutes=30,
             earliest_start=time(7, 0), assigned_pet_id="pet_001")
    b = Task(task_id="b", name="Play", duration_minutes=20,
             earliest_start=time(7, 30), assigned_pet_id="pet_001")

    assert a.conflicts_with(b) is False
    assert Scheduler(tasks=[a, b]).has_conflicts() is False


def test_conflict_warning_is_lightweight_and_nonraising():
    """conflict_warning returns '' when clear and a message when clashing."""
    clean = Scheduler(
        tasks=[
            Task(task_id="a", name="Walk", duration_minutes=30,
                 earliest_start=time(7, 0), assigned_pet_id="p1"),
            Task(task_id="b", name="Feed", duration_minutes=10,
                 earliest_start=time(8, 0), assigned_pet_id="p1"),
        ]
    )
    # No conflicts -> falsy empty string, so `if msg:` simply skips.
    assert clean.conflict_warning() == ""

    clashing = Scheduler(
        tasks=[
            Task(task_id="a", name="Walk", duration_minutes=30,
                 earliest_start=time(7, 0), assigned_pet_id="p1"),
            Task(task_id="b", name="Feed", duration_minutes=10,
                 earliest_start=time(7, 15), assigned_pet_id="p1"),
        ]
    )
    msg = clashing.conflict_warning()
    assert msg  # truthy, non-empty
    assert "conflict" in msg.lower()
    assert "Walk" in msg and "Feed" in msg


def test_sort_by_time_returns_chronological_order():
    """sort_by_time returns tasks in chronological order regardless of insertion."""
    # Added deliberately OUT of order: evening, morning, afternoon.
    scheduler = Scheduler(
        tasks=[
            Task(task_id="t_pm", name="Evening Play", duration_minutes=20,
                 earliest_start=time(19, 0), assigned_pet_id="p1"),
            Task(task_id="t_am", name="Morning Walk", duration_minutes=30,
                 earliest_start=time(7, 0), assigned_pet_id="p1"),
            Task(task_id="t_noon", name="Afternoon Meds", duration_minutes=5,
                 earliest_start=time(14, 30), assigned_pet_id="p1"),
        ]
    )

    ordered = scheduler.sort_by_time()

    assert [t.task_id for t in ordered] == ["t_am", "t_noon", "t_pm"]
    # The start times are non-decreasing.
    starts = [t.earliest_start for t in ordered]
    assert starts == sorted(starts)


def test_conflict_detection_flags_duplicate_times():
    """Two tasks scheduled at the exact same time are flagged as a conflict."""
    scheduler = Scheduler(
        tasks=[
            Task(task_id="walk", name="Walk", duration_minutes=30,
                 earliest_start=time(8, 0), assigned_pet_id="p1"),
            Task(task_id="meds", name="Meds", duration_minutes=10,
                 earliest_start=time(8, 0), assigned_pet_id="p2"),  # same 08:00
        ]
    )

    assert scheduler.has_conflicts() is True
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    ids = {conflicts[0].task_a.task_id, conflicts[0].task_b.task_id}
    assert ids == {"walk", "meds"}


if __name__ == "__main__":
    # Minimal runner so the file works even without pytest.
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS  {name}")
            except AssertionError as exc:
                failures += 1
                print(f"FAIL  {name}: {exc}")
    print(f"\n{'All tests passed.' if not failures else f'{failures} test(s) failed.'}")
    sys.exit(1 if failures else 0)
