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

*How did you use AI tools during this project?*

I used AI across every phase: **design** (turning the scenario into a UML class
diagram and identifying entities/value objects), **scaffolding** (generating the
class skeletons with attributes and empty method stubs from the UML),
**implementation** (writing the scheduling algorithms — sorting, filtering,
conflict detection, and recurrence — one feature at a time), **debugging**
(diagnosing the weekly-recurrence date bug and a Streamlit test-harness quirk),
**refactoring** (simplifying `detect_conflicts()` for readability), and
**documentation** (keeping the diagrams, README, and tests in sync with the
code).

*What kinds of prompts or questions were most helpful?*

Small, specific, verifiable requests worked best — e.g. "add a `filter_tasks`
method that filters by pet or completion status" or "update main.py to add two
tasks at the same time and verify the warning prints." Asking the AI to **run
the code and show the output** turned each step into something I could confirm
rather than trust blindly. Open-ended "how could this be improved?" questions
were useful for surfacing options (like the sweep-line optimization), as long as
I made the final call.

**b. Judgment and verification**

*Describe one moment where you did not accept an AI suggestion as-is.*

The clearest case was the `spawn_next()` recurrence logic. The first version
reused `next_occurrence()`, which for a **weekly** task completed before its
time-of-day slot returned the *same day* instead of a week later. I caught this
in the terminal output and had it rewritten to always advance exactly one period
(+1 day for daily, +7 for weekly) from the completed date. I also declined the
proposed sweep-line optimization for conflict detection to avoid unnecessary
complexity at this scale.

*How did you evaluate or verify what the AI suggested?*

I relied on **running things, not reading things**: the `pytest` suite (9 tests
covering sorting, recurrence, and conflict detection), `python main.py` for a
full end-to-end trace, and boundary checks (e.g. confirming daily recurrence
handled month-end, year-end, and leap-day correctly via `timedelta`). For the
UML, I verified with a script that diffed the diagram's methods against the
actual classes rather than eyeballing it.

**c. Claude Code workflow**

*Which Claude Code features were most effective for building your scheduler?*

The tight **edit → run → verify loop** was the most valuable. After almost every
change, the assistant ran `python main.py` and `python -m pytest` (and drove the
Streamlit app headlessly with `AppTest`) and read the output, so bugs surfaced
immediately instead of piling up. This caught real issues early — a weekly-
recurrence date that resolved to the wrong day, a Windows console encoding
problem with an em-dash, and a Streamlit `format_func` quirk in the test
harness. **Multi-file consistency edits** were also effective: when the code
changed, the same feature could be propagated to the tests, the four Mermaid
diagram files, and the README in one pass, keeping the design and docs in sync.
Finally, being able to **inspect the code programmatically** (e.g. using
`inspect` to diff the diagram's methods against the actual classes) turned
"does the UML still match?" into a verifiable check rather than a guess.

*Give one example of an AI suggestion you rejected or modified to keep your
system design clean.*

When asked how `detect_conflicts()` could be improved, the AI offered a
**sweep-line optimization** (sort by start time, stop scanning once tasks are
past the current one's end) to drop it from O(n²) to roughly O(n log n). I
**rejected that change** and kept the simpler `itertools.combinations` version,
because for a household's handful of daily tasks the quadratic cost is
irrelevant and the sweep-line adds real complexity — a classic premature
optimization. I applied only the readability refactor. Separately, I **modified**
an AI-written `spawn_next()` that reused `next_occurrence()`: for a weekly task
completed before its time slot it produced the *same day* instead of next week,
so I changed it to always advance exactly one period from the completed date.

*How did using separate chat sessions for different phases help you stay
organized?*

Splitting the work into phase-scoped sessions — **design/UML, class skeletons,
scheduling logic, testing, the Streamlit UI, and documentation** — kept each
conversation focused on one concern. Each session started with a clear goal and
a small, relevant slice of context, which made the assistant's suggestions more
on-target and made it easy for me to review changes without wading through
unrelated history. It also created natural checkpoints: I finished and verified
one phase (e.g. all tests passing) before moving to the next, and I could return
to an earlier phase — like resyncing the UML after the code grew — without
losing the thread of the current work.

---

## 4. Testing and Verification

**a. What you tested**

*What behaviors did you test?*

The suite in `tests/test_pawpal.py` has **9 tests** run with `python -m pytest`,
focused on the core scheduling logic:

- **Task completion** — `mark_completed()` flips a task from pending to done
  (`is_completed()` reflects the change).
- **Adding tasks** — `Pet.add_task()` increases the pet's task count.
- **Sorting correctness** — `Scheduler.sort_by_time()` returns tasks in
  chronological order regardless of the order they were added.
- **Recurrence** — completing a daily task auto-creates the next-day
  occurrence; a non-recurring task spawns nothing.
- **Conflict detection** — overlaps are flagged within a single pet and across
  different pets, including exact duplicate start times; windows that merely
  touch (one ends as the next begins) are correctly *not* flagged.
- **Lightweight conflict warning** — `conflict_warning()` returns a message
  when there are clashes and an empty string when clear (it never raises).

*Why were these tests important?*

These are the behaviors most likely to break silently and most central to the
app's value. Sorting, conflict detection, and recurrence each involve edge
cases (timeless tasks, touching vs. overlapping windows, month/leap-year date
math) where an off-by-one or boundary mistake would produce a plausible-looking
but wrong schedule. Testing them locks in correctness so later refactors — like
simplifying `detect_conflicts()` — can be verified instantly instead of
re-checked by hand.

**b. Confidence**

*How confident are you that your scheduler works correctly?*

**⭐⭐⭐⭐☆ (4 / 5).** All 9 tests pass and cover the core logic plus its tricky
edge cases (touching windows, duplicate times, cross-pet conflicts, leap-year
recurrence). I verified end-to-end with `main.py` and drove the Streamlit UI
headlessly, so the pieces work together, not just in isolation. It isn't a full
5 because several methods are still unimplemented stubs (`find_free_slot`,
`is_overdue`, `to_dict`/`from_dict`) and aren't exercised.

*What edge cases would you test next if you had more time?*

- **Owner availability** — scheduling a task outside the owner's available
  windows (once `find_free_slot` is implemented).
- **Overflow** — more tasks than fit in a day, so `resolve_conflicts()` pushes
  tasks past midnight.
- **Recurrence beyond daily/weekly** — unsupported frequencies, and a task
  completed *after* its scheduled time.
- **Overdue detection** — `is_overdue()` around the exact boundary time.
- **Serialization round-trip** — `to_dict()` → `from_dict()` preserves state.

---

## 5. Reflection

**a. What went well**

*What part of this project are you most satisfied with?*

The **scheduling logic and its test coverage**. Sorting, filtering, conflict
detection, and daily/weekly recurrence all work together, are backed by 9
passing tests, and handle real edge cases — touching-vs-overlapping time
windows, cross-pet conflicts, and leap-year-safe recurrence dates. I'm also
satisfied that the design stayed coherent as it grew: promoting `Scheduler` to
a central orchestrator kept the behavior out of the data classes, and the code,
tests, UML diagrams, and README all ended up in sync rather than drifting apart.

**b. What you would improve**

*If you had another iteration, what would you improve or redesign?*

I'd implement the methods that are still stubs so the model is complete:
**owner-availability-aware scheduling** (`find_free_slot`, so the plan respects
when the owner is actually free), **overdue detection** (`is_overdue`), and
**serialization** (`to_dict`/`from_dict`, so owners/pets/tasks can be saved and
reloaded). I'd also let `Task` reference its `Pet` directly (or store a real
back-reference) instead of only an `assigned_pet_id` string, and expand
recurrence beyond daily/weekly. Finally, the conflict *resolution* just pushes
tasks later; a smarter version would weigh priority so a high-priority task
isn't bumped by a low-priority one.

**c. Key takeaway**

*What is one important thing you learned about designing systems or working with
AI on this project?*

**Design first, then let the skeleton drive the code — and verify every AI
suggestion by running it.** Starting from a UML diagram meant the classes and
responsibilities were decided before any logic was written, which kept the
implementation focused. And the AI was most useful not when it wrote code, but
when it *ran* that code and showed the output: that loop is what caught the
weekly-recurrence bug and let me confidently reject a "faster" algorithm that
wasn't worth the complexity. AI accelerates the work, but the judgment about
what to keep — and the tests that prove it — have to stay with me.
