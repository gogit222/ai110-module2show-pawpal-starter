# Entities & Attributes

This document lists the core entities for PawPal+ and their attributes, with short definitions and examples.

## Owner
- **owner_id** (string): Unique identifier for the owner. Example: `owner_001`.
- **name** (string): Full name of the owner. Example: `Alex Morgan`.
- **contact** (object): Contact info such as `email` and `phone`. Example: `{"email": "alex@example.com", "phone": "+1-555-0123"}`.
- **availability** (list of time windows): Daily availability or schedule constraints. Example: `[{"day": "Mon-Fri", "start": "18:00", "end": "20:00"}]`.
- **preferences** (object): Owner preferences such as preferred walk times or feeding style. Example: `{"walk_times": ["07:00","18:00"], "feed_in_person": true}`.
- **timezone** (string): Time zone used for scheduling. Example: `America/Los_Angeles`.
- **location** (object/string): Address or coordinates. Example: `{"address": "123 Maple St", "lat": 47.6, "lng": -122.3}`.
- **emergency_contact** (object): Name and phone for emergencies. Example: `{"name":"Taylor Park", "phone":"+1-555-0987"}`.
- **notes** (string): Freeform notes about owner. Example: `Prefers short walks in hot weather.`

### Methods (Owner)
- `add_pet(pet: Pet) -> None`: Link a new pet to the owner. Example: `owner.add_pet(biscuit)`.
- `remove_pet(pet_id: str) -> None`: Unlink a pet. Example: `owner.remove_pet("pet_001")`.
- `update_availability(windows: list) -> None`: Replace or merge availability windows.
- `get_pets() -> list[Pet]`: Return pets owned by this owner.
- `get_upcoming_tasks(start: datetime, end: datetime) -> list[Task]`: Fetch tasks across owned pets in a time range.
- `notify(message: str) -> None`: Send a notification (email/SMS) to contact.
- `update_preferences(prefs: dict) -> None`: Update owner preference settings.
- `to_dict() / from_dict(data: dict)` : Serialization helpers.

## Pet
- **pet_id** (string): Unique identifier for the pet. Example: `pet_001`.
- **name** (string): Pet's name. Example: `Biscuit`.
- **species** (string): Species type (dog, cat, etc.). Example: `dog`.
- **breed** (string): Breed or type. Example: `Golden Retriever`.
- **birthdate / age** (date or int): Birthdate or age in years. Example: `2019-04-15` or `7`.
- **weight_kg** (number): Weight for dosing/activity planning. Example: `27.5`.
- **activity_level** (enum): Low / Medium / High. Example: `High`.
- **medical_conditions** (list): Conditions or allergies. Example: `["hip dysplasia"]`.
- **medications** (list of objects): Medication name, dose, times. Example: `[{"name":"Carprofen","dose":"50mg","times":["08:00","20:00"]}]`.
- **feeding_schedule** (list): Preferred or required feeding times. Example: `[{"time":"08:00","portion":"1 cup"}]`.
- **grooming_requirements** (object): Frequency/details. Example: `{"brushing_per_week":3}`.
- **preferences** (object): Likes/dislikes or behavioral notes. Example: `{"likes":"squeaky toys","dislikes":"baths"}`.
- **microchip_id** (string, optional): Example: `981020000123456`.

### Methods (Pet)
- `add_medication(med: dict) -> None`: Add a medication entry.
- `remove_medication(med_name: str) -> None`: Remove medication by name.
- `update_feeding_schedule(schedule: list) -> None`: Replace feeding schedule.
- `record_weight(weight_kg: float, date: date) -> None`: Record weight history.
- `is_medication_due(now: datetime) -> list[Medication]`: Return medications due at the given time.
- `needs_grooming() -> bool`: Simple heuristic based on `grooming_requirements` and last grooming.
- `next_feeding_time(now: datetime) -> datetime | None`: Compute next feeding time.
- `to_dict() / from_dict(data: dict)` : Serialization helpers.

## Task
- **task_id** (string): Unique identifier for the task. Example: `task_042`.
- **name** (string): Short title. Example: `Morning Walk`.
- **description** (string): Detailed instructions. Example: `30-minute brisk walk around the park.`
- **duration_minutes** (int): Estimated duration in minutes. Example: `30`.
- **priority** (enum or int): Priority level (high/medium/low) or numeric rank. Example: `high` or `3`.
- **earliest_start** (time) / **latest_end** (time): Scheduling window constraints. Example: `earliest_start: 06:00, latest_end: 09:00`.
- **recurrence** (object/null): Recurrence rule (daily/weekly/custom). Example: `{"freq":"daily"}`.
- **assigned_pet_id** (string): ID of the pet this task applies to. Example: `pet_001`.
- **requires_owner** (boolean): Whether owner presence is required. Example: `true`.
- **requires_equipment** (list): Items needed e.g., `leash`, `medication_pill_box`.
- **is_optional** (boolean): Whether the task can be skipped if time is short. Example: `false`.
- **last_completed** (timestamp/null): When task was last done. Example: `2026-06-22T18:12:00Z`.
- **tags** (list): Categorization (feeding, walk, medication). Example: `["feeding","high-priority"]`.
- **estimated_energy_cost** (optional number): Relative effort for pet (e.g., low/medium/high or numeric). Example: `"medium"` or `1.5`.

### Methods (Task)
- `schedule(start_time: datetime) -> ScheduledSlot`: Reserve a start time for this task and return the scheduled slot.
- `reschedule(new_start: datetime) -> ScheduledSlot`: Move the task to a new time.
- `mark_completed(timestamp: datetime) -> None`: Set `last_completed` and update recurrence state.
- `is_overdue(now: datetime) -> bool`: True if task had to be completed before `now` and wasn't.
- `conflicts_with(other: Task) -> bool`: Determine if time windows/duration overlap.
- `next_occurrence(after: datetime) -> datetime | None`: Compute the next run based on `recurrence`.
- `estimate_end(start_time: datetime) -> datetime`: Helper to compute end time from `duration_minutes`.
- `to_dict() / from_dict(data: dict)` : Serialization helpers.

---

Notes and usage:
- Use `owner_id`, `pet_id`, and `task_id` as primary keys to link records.
- Keep times in owner `timezone` and store timestamps in ISO8601 UTC when persisting.
- Model `recurrence` using a simple pattern object for now; expand later to RFC 5545 rules if needed.
