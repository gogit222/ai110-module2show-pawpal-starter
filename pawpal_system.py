"""PawPal+ system skeleton.

Class skeleton generated from the UML class diagram
(see diagrams/entities_class_diagram.mmd and Entities&Attributes.md).

This file contains names, attributes, and empty method stubs only.
Method bodies raise NotImplementedError so callers fail loudly until
each behavior is implemented.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
from enum import Enum
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
        self.owner_id = owner_id
        self.name = name
        self.contact = contact
        self.availability: list[Availability] = availability or []
        self.preferences = preferences
        self.timezone = timezone
        self.location = location
        self.emergency_contact = emergency_contact
        self.notes = notes

    def add_pet(self, pet: "Pet") -> None:
        raise NotImplementedError

    def remove_pet(self, pet_id: str) -> None:
        raise NotImplementedError

    def update_availability(self, windows: list[Availability]) -> None:
        raise NotImplementedError

    def get_pets(self) -> list["Pet"]:
        raise NotImplementedError

    def get_upcoming_tasks(self, start: datetime, end: datetime) -> list["Task"]:
        raise NotImplementedError

    def notify(self, message: str) -> None:
        raise NotImplementedError

    def update_preferences(self, prefs: Preferences) -> None:
        raise NotImplementedError

    def to_dict(self) -> dict:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: dict) -> "Owner":
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
    ) -> None:
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

    def add_medication(self, med: Medication) -> None:
        raise NotImplementedError

    def remove_medication(self, med_name: str) -> None:
        raise NotImplementedError

    def update_feeding_schedule(self, schedule: list[Feeding]) -> None:
        raise NotImplementedError

    def record_weight(self, weight_kg: float, date: date) -> None:
        raise NotImplementedError

    def is_medication_due(self, now: datetime) -> list[Medication]:
        raise NotImplementedError

    def needs_grooming(self) -> bool:
        raise NotImplementedError

    def next_feeding_time(self, now: datetime) -> Optional[datetime]:
        raise NotImplementedError

    def to_dict(self) -> dict:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
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
        raise NotImplementedError

    def reschedule(self, new_start: datetime) -> ScheduledSlot:
        raise NotImplementedError

    def mark_completed(self, timestamp: datetime) -> None:
        raise NotImplementedError

    def is_overdue(self, now: datetime) -> bool:
        raise NotImplementedError

    def conflicts_with(self, other: "Task") -> bool:
        raise NotImplementedError

    def next_occurrence(self, after: datetime) -> Optional[datetime]:
        raise NotImplementedError

    def estimate_end(self, start_time: datetime) -> datetime:
        raise NotImplementedError

    def to_dict(self) -> dict:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        raise NotImplementedError
