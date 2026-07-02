# PawPal+ Project Reflection

## 1. System Design

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Entities identified are :

- Owner
- Pet
- Task

Algorithmic logic is required for sorting, conflict detection, and recurring task management.

**a. Initial design**

- Briefly describe your initial UML design.

The UML design (diagrams/entities_class_diagram.mmd) is a class diagram for PawPal+, a pet-care scheduling app. It has three layers:

Core domain classes (rich, with attributes + behavior):

Owner — a pet owner with contact, availability, preferences, and location; manages pets and their upcoming tasks.
Pet — an animal with medical/feeding/grooming data; answers questions like "is medication due?" and "does it need grooming?"
Task — a scheduled care activity (walk, feeding, meds) with a duration, priority, time window, and recurrence; handles scheduling, conflict detection, and overdue checks.
Value objects (data-only): Contact, Availability, Preferences, Location, Medication, Feeding, Grooming, Recurrence — composed into the core classes.

Enumerations: Priority (HIGH/MEDIUM/LOW) and ActivityLevel (LOW/MEDIUM/HIGH).

Relationships:

Owner owns 0..* Pets (aggregation)
Pet has 0..* Tasks (aggregation)
Task is assigned_to exactly 1 Pet, and Owner creates Tasks
Value objects attach via composition (filled diamond); enums via directed association.

- What classes did you include, and what responsibilities did you assign to each?

Core classes and their methods
Owner — Entities&Attributes.md:16-24
add_pet(pet) — link a new pet
remove_pet(pet_id) — unlink a pet
update_availability(windows) — replace/merge availability windows
get_pets() → Pet[]
get_upcoming_tasks(start, end) → Task[] across owned pets
notify(message) — send email/SMS
update_preferences(prefs)
to_dict() / from_dict(data) — serialization
Pet — Entities&Attributes.md:41-49
add_medication(med) / remove_medication(med_name)
update_feeding_schedule(schedule)
record_weight(weight_kg, date)
is_medication_due(now) → Medication[]
needs_grooming() → bool
next_feeding_time(now) → datetime | None
to_dict() / from_dict(data)
Task — Entities&Attributes.md:67-75
schedule(start_time) → ScheduledSlot
reschedule(new_start) → ScheduledSlot
mark_completed(timestamp)
is_overdue(now) → bool
conflicts_with(other) → bool
next_occurrence(after) → datetime | None
estimate_end(start_time) → datetime
to_dict() / from_dict(data)
Supporting value objects (data-only, no methods)
Contact, Availability, Preferences, Location, Medication, Feeding, Grooming, Recurrence — these hold attributes only.

Enumerations
Priority — HIGH / MEDIUM / LOW
ActivityLevel — LOW / MEDIUM / HIGH
Relationships (from the class diagram)
Owner owns 0..* Pet; Owner creates 0..* Task
Pet has 0..* Task; a Task is assigned_to exactly 1 Pet


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

Change
Refactored Scheduler.detect_conflicts() in pawpal_system.py to replace a nested index-based loop with an itertools.combinations list comprehension.

Before — manual double loop with index bookkeeping and .append():


for i in range(len(timed)):
    for j in range(i + 1, len(timed)):
        a, b = timed[i], timed[j]
        if a.conflicts_with(b):
            conflicts.append(Conflict(...))
After — a comprehension that reads as its intent ("every unordered pair that conflicts"):


return [
    Conflict(a, b, same_pet=a.assigned_pet_id == b.assigned_pet_id)
    for a, b in combinations(timed, 2)
    if a.conflicts_with(b)
]
Added from itertools import combinations. Verified: all 7 tests pass and main.py's conflict warning is unchanged.

Tradeoff
Gained: readability. Intent is explicit, the off-by-one risk of range(i + 1, len) is gone, and there's less boilerplate.
Cost: a new stdlib import, and the logic is now a single expression (slightly harder to drop a debugger breakpoint or log mid-loop than with explicit statements).
Unchanged: correctness and performance. It's still O(n²) — combinations generates the same n·(n−1)/2 pairs; this was purely a clarity refactor, not a speedup.

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
