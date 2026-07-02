"""PawPal+ testing ground.

Quick end-to-end sanity check of the domain model:
  - build an Owner with two Pets
  - add Tasks deliberately OUT of time order (and mark one completed)
  - exercise Scheduler.sort_by_time() and Scheduler.filter_tasks()
  - print Today's Schedule

Run with:  python main.py
"""

from datetime import date, datetime, time

from pawpal_system import (
    Owner,
    Pet,
    Task,
    Scheduler,
    Recurrence,
    Priority,
    ActivityLevel,
)


def build_owner() -> Owner:
    owner = Owner(owner_id="owner_001", name="Alex Morgan")

    biscuit = Pet(
        pet_id="pet_001",
        name="Biscuit",
        species="dog",
        breed="Golden Retriever",
        activity_level=ActivityLevel.HIGH,
    )
    mochi = Pet(
        pet_id="pet_002",
        name="Mochi",
        species="cat",
        breed="Tabby",
        activity_level=ActivityLevel.LOW,
    )

    # Tasks added OUT of time order on purpose (evening, morning, afternoon,
    # breakfast) so sorting has something to fix.
    mochi.add_task(
        Task(
            task_id="task_004",
            name="Evening Play / Enrichment",
            duration_minutes=20,
            priority=Priority.LOW,
            earliest_start=time(19, 0),
            assigned_pet_id=mochi.pet_id,
        )
    )
    biscuit.add_task(
        Task(
            task_id="task_001",
            name="Morning Walk",
            duration_minutes=30,
            priority=Priority.HIGH,
            earliest_start=time(7, 0),
            assigned_pet_id=biscuit.pet_id,
        )
    )
    biscuit.add_task(
        Task(
            task_id="task_003",
            name="Afternoon Medication",
            duration_minutes=5,
            priority=Priority.HIGH,
            earliest_start=time(14, 30),
            assigned_pet_id=biscuit.pet_id,
        )
    )
    mochi.add_task(
        Task(
            task_id="task_002",
            name="Breakfast Feeding",
            duration_minutes=10,
            priority=Priority.MEDIUM,
            earliest_start=time(8, 0),
            assigned_pet_id=mochi.pet_id,
        )
    )
    # Deliberate clash: Mochi's meds at 07:00 collide with Biscuit's 07:00
    # Morning Walk (different pets, same time) to exercise conflict detection.
    mochi.add_task(
        Task(
            task_id="task_005",
            name="Morning Medication",
            duration_minutes=5,
            priority=Priority.HIGH,
            earliest_start=time(7, 0),
            assigned_pet_id=mochi.pet_id,
        )
    )

    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    # Mark the morning walk as already done so completion filters have data.
    biscuit.get_tasks()[0].mark_completed(datetime(2026, 7, 2, 7, 35))
    return owner


def _fmt(task: Task) -> str:
    when = task.earliest_start.strftime("%H:%M") if task.earliest_start else "--:--"
    status = "done" if task.is_completed() else "pending"
    pri = task.priority.value if task.priority else "-"
    return f"{when}  {task.name:<28} [{status:<7}] (priority: {pri})"


def print_insertion_order(scheduler: Scheduler) -> None:
    print("\n=== Tasks in INSERTION order (as added) ===")
    for t in scheduler.tasks:
        print("  " + _fmt(t))


def print_sorted_by_time(scheduler: Scheduler) -> None:
    print("\n=== Tasks sorted by time (Scheduler.sort_by_time) ===")
    for t in scheduler.sort_by_time():
        print("  " + _fmt(t))


def print_filtered(scheduler: Scheduler) -> None:
    print("\n=== Filtering (Scheduler.filter_tasks) ===")
    pending = scheduler.filter_tasks(completed=False)
    completed = scheduler.filter_tasks(completed=True)
    mochi_tasks = scheduler.filter_tasks(pet_name="Mochi")
    print(f"  pending only   ({len(pending)}): {[t.name for t in pending]}")
    print(f"  completed only ({len(completed)}): {[t.name for t in completed]}")
    print(f"  Mochi's tasks  ({len(mochi_tasks)}): {[t.name for t in mochi_tasks]}")


def print_recurrence_demo() -> None:
    """Show that completing a recurring task auto-creates the next one."""
    print("\n=== Recurrence: completing a task spawns the next occurrence ===")
    owner = Owner(owner_id="owner_002", name="Sam")
    pet = Pet(pet_id="pet_010", name="Rex", species="dog")
    walk = Task(
        task_id="daily_walk",
        name="Daily Walk",
        duration_minutes=30,
        priority=Priority.HIGH,
        earliest_start=time(7, 0),
        recurrence=Recurrence(freq="daily"),
        assigned_pet_id=pet.pet_id,
    )
    pet.add_task(walk)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    scheduler.load_tasks_from_owner()
    print("  before complete:", [t.task_id for t in pet.get_tasks()])

    upcoming = scheduler.complete_task(walk, datetime(2026, 7, 2, 7, 35))
    print(
        f"  completed '{walk.task_id}' -> spawned '{upcoming.task_id}' "
        f"(pending, starts {upcoming.earliest_start.strftime('%H:%M')})"
    )
    print("  after complete :", [t.task_id for t in pet.get_tasks()])


def print_conflict_check(scheduler: Scheduler) -> None:
    """Run the lightweight conflict check on the given scheduler's tasks."""
    print("\n=== Conflict check (Scheduler.conflict_warning) ===")
    # Lightweight strategy: get a warning message instead of raising.
    warning = scheduler.conflict_warning()
    if warning:
        for line in warning.splitlines():
            print("  " + line)
    else:
        print("  No conflicts.")
    print("  (program continues normally after the warning)")


def print_todays_schedule(owner: Owner, today: date) -> None:
    scheduler = Scheduler(owner=owner)
    scheduler.load_tasks_from_owner()
    plan = scheduler.get_plan_for_day(today)

    tasks = {t.task_id: t for t in scheduler.tasks}
    pets = {p.pet_id: p for p in owner.get_pets()}

    print(f"\n=== Today's Schedule - {today.isoformat()} ({owner.name}) ===")
    if not plan:
        print("  (nothing scheduled)")
        return

    for slot in plan:
        task = tasks[slot.task_id]
        pet = pets.get(task.assigned_pet_id)
        pet_name = pet.name if pet else "?"
        start = slot.start_time.strftime("%H:%M")
        end = slot.end_time.strftime("%H:%M")
        priority = task.priority.value if task.priority else "-"
        print(
            f"  {start}-{end}  {task.name:<28} "
            f"[{pet_name}]  (priority: {priority})"
        )
    print(f"\n  {len(plan)} task(s) scheduled.\n")


def main() -> None:
    owner = build_owner()

    scheduler = Scheduler(owner=owner)
    scheduler.load_tasks_from_owner()

    print_insertion_order(scheduler)
    print_sorted_by_time(scheduler)
    print_filtered(scheduler)
    print_recurrence_demo()
    print_conflict_check(scheduler)
    print_todays_schedule(owner, date.today())


if __name__ == "__main__":
    main()
