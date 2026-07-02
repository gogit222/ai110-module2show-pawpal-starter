"""PawPal+ system skeleton.

Class skeleton generated from the UML class diagram
(see diagrams/entities_class_diagram.mmd and Entities&Attributes.md).

Core scheduling logic is implemented; remaining behaviors are stubs that
raise NotImplementedError so callers fail loudly until each is built out.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import Enum
from itertools import combinations
from typing import Optional


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------
class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ActivityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# ---------------------------------------------------------------------------
# Supporting / value objects (data-only)
# ---------------------------------------------------------------------------
@dataclass
class Contact:
    email: str = ""
    phone: str = ""


@dataclass
class Availability:
    day: str = ""
    start: Optional[time] = None
    end: Optional[time] = None


@dataclass
class Preferences:
    walk_times: list[str] = field(default_factory=list)
    feed_in_person: bool = False


@dataclass
class Location:
    address: str = ""
    lat: Optional[float] = None
    lng: Optional[float] = None


@dataclass
class Medication:
    name: str = ""
    dose: str = ""
    times: list[time] = field(default_factory=list)


@dataclass
class Feeding:
    time: Optional[time] = None
    portion: str = ""


@dataclass
class Grooming:
    brushing_per_week: int = 0


@dataclass
class Recurrence:
    freq: str = ""
    rule: str = ""


@dataclass
class ScheduledSlot:
    """Result of scheduling a task (referenced by Task.schedule/reschedule)."""

    task_id: str = ""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


@dataclass
class Conflict:
    """A pair of tasks whose time windows overlap.

    ``same_pet`` is True when both tasks belong to the same pet.
    """

    task_a: "Task"
    task_b: "Task"
    same_pet: bool


# ---------------------------------------------------------------------------
# Core domain classes
# ---------------------------------------------------------------------------
class Owner:
    def __init__(
        self,
        owner_id: str,
        name: str,
        contact: Optional[Contact] = None,
        availability: Optional[list[Availability]] = None,
        preferences: Optional[Preferences] = None,
        timezone: str = "",
        location: Optional[Location] = None,
        emergency_contact: Optional[Contact] = None,
        notes: str = "",
    ) -> None:
        """Create an owner and initialize an empty list of pets."""
        self.owner_id = owner_id
        self.name = name
        self.contact = contact
        self.availability: list[Availability] = availability or []
        self.preferences = preferences
        self.timezone = timezone
        self.location = location
        self.emergency_contact = emergency_contact
        self.notes = notes
        self.pets: list["Pet"] = []

    def add_pet(self, pet: "Pet") -> None:
        """Link a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        """Unlink the pet with the given id from this owner."""
        self.pets = [p for p in self.pets if p.pet_id != pet_id]

    def update_availability(self, windows: list[Availability]) -> None:
        """Replace this owner's availability windows."""
        raise NotImplementedError

    def get_pets(self) -> list["Pet"]:
        """Return a copy of the owner's pets."""
        return list(self.pets)

    def get_upcoming_tasks(self, start: datetime, end: datetime) -> list["Task"]:
        """Return tasks across all pets falling within the time range."""
        raise NotImplementedError

    def notify(self, message: str) -> None:
        """Send a notification (email/SMS) to this owner."""
        raise NotImplementedError

    def update_preferences(self, prefs: Preferences) -> None:
        """Update this owner's preference settings."""
        raise NotImplementedError

    def to_dict(self) -> dict:
        """Serialize this owner to a plain dict."""
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: dict) -> "Owner":
        """Build an Owner from a serialized dict."""
        raise NotImplementedError


class Pet:
    def __init__(
        self,
        pet_id: str,
        name: str,
        species: str = "",
        breed: str = "",
        birthdate: Optional[date] = None,
        weight_kg: Optional[float] = None,
        activity_level: Optional[ActivityLevel] = None,
        medical_conditions: Optional[list[str]] = None,
        medications: Optional[list[Medication]] = None,
        feeding_schedule: Optional[list[Feeding]] = None,
        grooming_requirements: Optional[Grooming] = None,
        preferences: Optional[Preferences] = None,
        microchip_id: str = "",
        tasks: Optional[list["Task"]] = None,
    ) -> None:
        """Create a pet with its care details and an optional task list."""
        self.pet_id = pet_id
        self.name = name
        self.species = species
        self.breed = breed
        self.birthdate = birthdate
        self.weight_kg = weight_kg
        self.activity_level = activity_level
        self.medical_conditions: list[str] = medical_conditions or []
        self.medications: list[Medication] = medications or []
        self.feeding_schedule: list[Feeding] = feeding_schedule or []
        self.grooming_requirements = grooming_requirements
        self.preferences = preferences
        self.microchip_id = microchip_id
        self.tasks: list["Task"] = tasks or []

    def add_task(self, task: "Task") -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def get_tasks(self) -> list["Task"]:
        """Return a copy of this pet's tasks."""
        return list(self.tasks)

    def add_medication(self, med: Medication) -> None:
        """Add a medication entry to this pet."""
        raise NotImplementedError

    def remove_medication(self, med_name: str) -> None:
        """Remove a medication from this pet by name."""
        raise NotImplementedError

    def update_feeding_schedule(self, schedule: list[Feeding]) -> None:
        """Replace this pet's feeding schedule."""
        raise NotImplementedError

    def record_weight(self, weight_kg: float, date: date) -> None:
        """Record a weight measurement for this pet on a given date."""
        raise NotImplementedError

    def is_medication_due(self, now: datetime) -> list[Medication]:
        """Return medications due at the given time."""
        raise NotImplementedError

    def needs_grooming(self) -> bool:
        """Return True if the pet is due for grooming."""
        raise NotImplementedError

    def next_feeding_time(self, now: datetime) -> Optional[datetime]:
        """Return the next feeding time after now, or None."""
        raise NotImplementedError

    def to_dict(self) -> dict:
        """Serialize this pet to a plain dict."""
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        """Build a Pet from a serialized dict."""
        raise NotImplementedError


class Task:
    def __init__(
        self,
        task_id: str,
        name: str,
        description: str = "",
        duration_minutes: int = 0,
        priority: Optional[Priority] = None,
        earliest_start: Optional[time] = None,
        latest_end: Optional[time] = None,
        recurrence: Optional[Recurrence] = None,
        assigned_pet_id: str = "",
        requires_owner: bool = False,
        requires_equipment: Optional[list[str]] = None,
        is_optional: bool = False,
        last_completed: Optional[datetime] = None,
        tags: Optional[list[str]] = None,
        estimated_energy_cost: str = "",
    ) -> None:
        """Create a care task with its scheduling constraints and metadata."""
        self.task_id = task_id
        self.name = name
        self.description = description
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.earliest_start = earliest_start
        self.latest_end = latest_end
        self.recurrence = recurrence
        self.assigned_pet_id = assigned_pet_id
        self.requires_owner = requires_owner
        self.requires_equipment: list[str] = requires_equipment or []
        self.is_optional = is_optional
        self.last_completed = last_completed
        self.tags: list[str] = tags or []
        self.estimated_energy_cost = estimated_energy_cost

    def schedule(self, start_time: datetime) -> ScheduledSlot:
        """Reserve a start time and return the resulting scheduled slot."""
        return ScheduledSlot(
            task_id=self.task_id,
            start_time=start_time,
            end_time=self.estimate_end(start_time),
        )

    def reschedule(self, new_start: datetime) -> ScheduledSlot:
        """Move this task to a new start time and return the new slot."""
        raise NotImplementedError

    def mark_completed(self, timestamp: datetime) -> None:
        """Mark the task done by recording its completion timestamp."""
        # Completion status is represented by last_completed:
        # None means not yet done; a timestamp means done at that time.
        self.last_completed = timestamp

    def is_completed(self) -> bool:
        """Return True if the task has a recorded completion time."""
        return self.last_completed is not None

    def is_overdue(self, now: datetime) -> bool:
        """Return True if the task should have been completed before now."""
        raise NotImplementedError

    def conflicts_with(self, other: "Task") -> bool:
        """Return True if this task's time window overlaps another's.

        Windows are ``[earliest_start, earliest_start + duration)`` compared
        on a shared reference day. Tasks without an earliest_start never
        conflict, and windows that merely touch (one ends as the other
        starts) do not count as overlapping.
        """
        if self.earliest_start is None or other.earliest_start is None:
            return False
        ref = date.min
        a_start = datetime.combine(ref, self.earliest_start)
        a_end = a_start + timedelta(minutes=self.duration_minutes)
        b_start = datetime.combine(ref, other.earliest_start)
        b_end = b_start + timedelta(minutes=other.duration_minutes)
        return a_start < b_end and b_start < a_end

    def next_occurrence(self, after: datetime) -> Optional[datetime]:
        """Return the next start datetime after ``after`` per recurrence.

        Supports ``daily`` and ``weekly`` frequencies; returns None if the
        task does not recur (or uses an unsupported frequency).
        """
        if self.recurrence is None:
            return None
        step = {
            "daily": timedelta(days=1),
            "weekly": timedelta(weeks=1),
        }.get((self.recurrence.freq or "").lower())
        if step is None:
            return None
        anchor_time = self.earliest_start or after.time()
        candidate = datetime.combine(after.date(), anchor_time)
        while candidate <= after:
            candidate += step
        return candidate

    def spawn_next(self, completed_at: datetime) -> Optional["Task"]:
        """Build a fresh, uncompleted Task for the next occurrence.

        Returns None if this task does not recur daily/weekly. The new task
        copies this one's details, keeps the same recurrence, resets
        ``last_completed``, and is dated exactly one period (a day or a week)
        after the completed occurrence.
        """
        if self.recurrence is None:
            return None
        step = {
            "daily": timedelta(days=1),
            "weekly": timedelta(weeks=1),
        }.get((self.recurrence.freq or "").lower())
        if step is None:
            return None
        nxt = (
            datetime.combine(completed_at.date(), self.earliest_start or completed_at.time())
            + step
        )
        return Task(
            task_id=f"{self.task_id}#{nxt.date().isoformat()}",
            name=self.name,
            description=self.description,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            earliest_start=nxt.time(),
            latest_end=self.latest_end,
            recurrence=self.recurrence,
            assigned_pet_id=self.assigned_pet_id,
            requires_owner=self.requires_owner,
            requires_equipment=list(self.requires_equipment),
            is_optional=self.is_optional,
            last_completed=None,
            tags=list(self.tags),
            estimated_energy_cost=self.estimated_energy_cost,
        )

    def estimate_end(self, start_time: datetime) -> datetime:
        """Return the end time computed from start plus duration."""
        return start_time + timedelta(minutes=self.duration_minutes)

    def to_dict(self) -> dict:
        """Serialize this task to a plain dict."""
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Build a Task from a serialized dict."""
        raise NotImplementedError


class Scheduler:
    """Builds a conflict-free daily plan from tasks, honoring owner
    availability, task priority, and owner preferences."""

    def __init__(
        self,
        owner: Optional[Owner] = None,
        tasks: Optional[list[Task]] = None,
        availability: Optional[list[Availability]] = None,
    ) -> None:
        """Create a scheduler bound to an owner, task pool, and availability."""
        self.owner = owner
        self.tasks: list[Task] = tasks or []
        self.availability: list[Availability] = availability or []
        self.slots: list[ScheduledSlot] = []

    def load_tasks_from_owner(self) -> list[Task]:
        """Flatten every task across the owner's pets into self.tasks."""
        if self.owner is None:
            self.tasks = []
            return self.tasks
        self.tasks = [
            task for pet in self.owner.get_pets() for task in pet.get_tasks()
        ]
        return self.tasks

    def add_task(self, task: Task) -> None:
        """Add a single task to the scheduler's pool."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove a task from the pool by id."""
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

    def sort_by_time(self) -> list[Task]:
        """Return this scheduler's tasks sorted by their earliest_start time.

        Uses each Task's ``earliest_start`` attribute as the sort key; tasks
        without a time sort to the end.
        """
        return sorted(
            self.tasks,
            key=lambda task: (
                task.earliest_start is None,
                task.earliest_start or time.min,
            ),
        )

    def prioritize(self) -> list[Task]:
        """Return tasks ordered by earliest_start (None sorts last)."""
        return self.sort_by_time()

    def filter_tasks(
        self,
        completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
    ) -> list[Task]:
        """Return tasks filtered by completion status and/or pet name.

        - ``completed``: True keeps only done tasks, False only not-done,
          None keeps any.
        - ``pet_name``: keep only tasks assigned to the owner's pet(s) with
          this name (case-insensitive); None keeps any.
        Filters combine: passing both narrows to tasks matching both.
        """
        results = list(self.tasks)
        if completed is not None:
            results = [t for t in results if t.is_completed() == completed]
        if pet_name is not None:
            pets = self.owner.get_pets() if self.owner is not None else []
            pet_ids = {
                p.pet_id for p in pets if p.name.lower() == pet_name.lower()
            }
            results = [t for t in results if t.assigned_pet_id in pet_ids]
        return results

    def complete_task(self, task: Task, timestamp: datetime) -> Optional[Task]:
        """Mark a task complete and auto-create its next occurrence.

        For a recurring (daily/weekly) task, a fresh instance is spawned for
        the next occurrence, registered on the owning pet (so it persists)
        and added to this scheduler's task pool. Returns the new Task, or
        None if the task does not recur.
        """
        task.mark_completed(timestamp)
        upcoming = task.spawn_next(timestamp)
        if upcoming is None:
            return None
        if self.owner is not None:
            for pet in self.owner.get_pets():
                if pet.pet_id == task.assigned_pet_id:
                    pet.add_task(upcoming)
                    break
        self.tasks.append(upcoming)
        return upcoming

    def detect_conflicts(self) -> list[Conflict]:
        """Return every pair of tasks whose requested times overlap.

        Compares each task's ``earliest_start``/duration window against the
        others, so it catches clashes whether the tasks belong to the same
        pet or to different pets. Tasks without an earliest_start are
        ignored. Note this inspects the *requested* times, not the resolved
        plan (``generate_plan`` spreads conflicts apart).
        """
        timed = [t for t in self.tasks if t.earliest_start is not None]
        return [
            Conflict(
                task_a=a,
                task_b=b,
                same_pet=a.assigned_pet_id == b.assigned_pet_id,
            )
            for a, b in combinations(timed, 2)
            if a.conflicts_with(b)
        ]

    def has_conflicts(self) -> bool:
        """Return True if any two tasks have overlapping requested times."""
        return bool(self.detect_conflicts())

    def conflict_warning(self) -> str:
        """Return a human-readable warning describing any time conflicts.

        Lightweight and non-raising: returns an empty string when there are
        no conflicts, so callers can do ``if msg: warn(msg)`` and keep going
        instead of wrapping scheduling in try/except.
        """
        conflicts = self.detect_conflicts()
        if not conflicts:
            return ""
        lines = [f"Warning: {len(conflicts)} scheduling conflict(s) detected:"]
        for c in conflicts:
            scope = "same pet" if c.same_pet else "different pets"
            a, b = c.task_a, c.task_b
            a_t = a.earliest_start.strftime("%H:%M") if a.earliest_start else "??:??"
            b_t = b.earliest_start.strftime("%H:%M") if b.earliest_start else "??:??"
            lines.append(f"  - {a.name} ({a_t}) overlaps {b.name} ({b_t}) [{scope}]")
        return "\n".join(lines)

    def find_free_slot(self, task: Task, day: date) -> Optional[ScheduledSlot]:
        """Find an availability window that fits the task on the given day."""
        raise NotImplementedError

    def resolve_conflicts(self, slots: list[ScheduledSlot]) -> list[ScheduledSlot]:
        """Push overlapping slots later so no two tasks collide.

        Slots are processed in start-time order; each task keeps its
        duration but is delayed to begin no earlier than the previous
        task's end time.
        """
        ordered = sorted(
            (s for s in slots if s.start_time is not None),
            key=lambda s: s.start_time,
        )
        resolved: list[ScheduledSlot] = []
        prev_end: Optional[datetime] = None
        for slot in ordered:
            start = slot.start_time
            duration = (
                slot.end_time - slot.start_time
                if slot.end_time is not None
                else timedelta()
            )
            if prev_end is not None and start < prev_end:
                start = prev_end
            end = start + duration
            resolved.append(
                ScheduledSlot(task_id=slot.task_id, start_time=start, end_time=end)
            )
            prev_end = end
        return resolved

    def generate_plan(self, start: datetime, end: datetime) -> list[ScheduledSlot]:
        """Produce a non-overlapping schedule for the given time range.

        Each task is anchored at its ``earliest_start`` on the start date
        (falling back to ``start`` if unset), sorted chronologically, then
        passed through ``resolve_conflicts`` so no two tasks overlap.
        """
        day = start.date()
        plan: list[ScheduledSlot] = []
        for task in self.tasks:
            anchor = (
                datetime.combine(day, task.earliest_start)
                if task.earliest_start is not None
                else start
            )
            if start <= anchor <= end:
                plan.append(task.schedule(anchor))
        plan = self.resolve_conflicts(plan)
        self.slots = plan
        return plan

    def get_plan_for_day(self, day: date) -> list[ScheduledSlot]:
        """Return the scheduled slots for a single calendar day."""
        start = datetime.combine(day, time.min)
        end = datetime.combine(day, time.max)
        return self.generate_plan(start, end)

    def to_dict(self) -> dict:
        """Serialize this scheduler to a plain dict."""
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: dict) -> "Scheduler":
        """Build a Scheduler from a serialized dict."""
        raise NotImplementedError
