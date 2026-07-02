from datetime import date, datetime, time

import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler, Priority, Recurrence

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")

# --- Persistent domain objects in the session "vault" ---
# Build the Owner once per session (seeded with one pet) and reuse it across
# reruns. Streamlit re-runs this whole script on every interaction, so the
# "not in st.session_state" guard prevents rebuilding and wiping state.
if "owner" not in st.session_state:
    seeded = Owner(owner_id="owner_ui", name=owner_name)
    seeded.add_pet(Pet(pet_id="pet_001", name="Mochi", species="cat"))
    st.session_state.owner = seeded
    st.session_state.pet_seq = 1

owner = st.session_state.owner
owner.name = owner_name  # keep in sync with the input field

# ---------------------------------------------------------------------------
# Adding a Pet  ->  Owner.add_pet(Pet(...))
# ---------------------------------------------------------------------------
st.markdown("### Pets")
pcol1, pcol2, pcol3 = st.columns([2, 1, 1])
with pcol1:
    new_pet_name = st.text_input("New pet name", value="Biscuit")
with pcol2:
    new_pet_species = st.selectbox("Species", ["dog", "cat", "other"])
with pcol3:
    st.write("")  # vertical spacer to align the button with the inputs
    st.write("")
    if st.button("Add pet"):
        st.session_state.pet_seq += 1
        owner.add_pet(
            Pet(
                pet_id=f"pet_{st.session_state.pet_seq:03d}",
                name=new_pet_name,
                species=new_pet_species,
            )
        )

pets = owner.get_pets()
if not pets:
    st.info("Add a pet to get started.")
    st.stop()

selected_idx = st.selectbox(
    "Active pet (tasks below are added to this pet)",
    range(len(pets)),
    format_func=lambda i: f"{pets[i].name} ({pets[i].species})",
    key="active_pet_idx",
)
pet = pets[selected_idx]

# Removing a Pet  ->  Owner.remove_pet(pet_id)
if st.button(f"Remove {pet.name}"):
    owner.remove_pet(pet.pet_id)
    # Drop the stale selection index so the selectbox re-anchors to a valid pet.
    st.session_state.pop("active_pet_idx", None)
    st.rerun()

# ---------------------------------------------------------------------------
# Scheduling a Task  ->  Pet.add_task(Task(...))
# ---------------------------------------------------------------------------
st.markdown("### Tasks")
st.caption(f"Add care tasks for {pet.name}. They feed into the scheduler below.")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    earliest_start = st.time_input("Earliest start", value=time(7, 0))
with col5:
    repeats = st.selectbox("Repeats", ["none", "daily", "weekly"])

add_col, clear_col = st.columns(2)
with add_col:
    if st.button("Add task"):
        st.session_state.task_seq = st.session_state.get("task_seq", 0) + 1
        pet.add_task(
            Task(
                task_id=f"task_{st.session_state.task_seq:03d}",
                name=task_title,
                duration_minutes=int(duration),
                priority=Priority(priority),
                earliest_start=earliest_start,
                recurrence=(None if repeats == "none" else Recurrence(freq=repeats)),
                assigned_pet_id=pet.pet_id,
            )
        )
with clear_col:
    if st.button(f"Clear {pet.name}'s tasks"):
        pet.tasks.clear()

st.markdown("### Task list")
if not any(p.get_tasks() for p in pets):
    st.info("No tasks yet. Add one above.")
else:
    # Filters -> Scheduler.filter_tasks(...)
    fcol1, fcol2 = st.columns(2)
    with fcol1:
        status_filter = st.radio("Show", ["All", "Pending", "Completed"], horizontal=True)
    with fcol2:
        pet_filter = st.selectbox("Pet", ["All pets"] + [p.name for p in pets])

    board = Scheduler(owner=owner)
    board.load_tasks_from_owner()
    completed_arg = None if status_filter == "All" else (status_filter == "Completed")
    pet_arg = None if pet_filter == "All pets" else pet_filter
    # Filter, then show in time order.
    filtered = Scheduler(
        tasks=board.filter_tasks(completed=completed_arg, pet_name=pet_arg)
    ).sort_by_time()

    pets_by_id = {p.pet_id: p for p in pets}
    if not filtered:
        st.caption("No tasks match the current filter.")
    else:
        st.caption(f"{len(filtered)} task(s), sorted by time")
        header = st.columns([1, 1, 3, 2, 1])
        for col, label in zip(header, ["Done", "Time", "Task", "Pet", "Priority"]):
            col.markdown(f"**{label}**")
    for t in filtered:
        c_done, c_time, c_name, c_pet, c_pri = st.columns([1, 1, 3, 2, 1])
        with c_done:
            done = st.checkbox(
                "done",
                value=t.is_completed(),
                key=f"done_{t.task_id}",
                label_visibility="collapsed",
            )
        # Sync the model to the checkbox. Completing routes through
        # Scheduler.complete_task -> marks done and, if the task recurs,
        # auto-creates the next occurrence on the owning pet.
        if done and not t.is_completed():
            upcoming = board.complete_task(t, datetime.now())
            if upcoming is not None:
                st.toast(
                    f"'{t.name}' done - next occurrence added "
                    f"({upcoming.earliest_start.strftime('%H:%M')})."
                )
        elif not done and t.is_completed():
            t.last_completed = None
        with c_time:
            st.write(t.earliest_start.strftime("%H:%M") if t.earliest_start else "-")
        with c_name:
            repeat_tag = f" 🔁{t.recurrence.freq}" if t.recurrence else ""
            st.write((f"~~{t.name}~~" if t.is_completed() else t.name) + repeat_tag)
        with c_pet:
            owner_pet = pets_by_id.get(t.assigned_pet_id)
            st.write(owner_pet.name if owner_pet else "?")
        with c_pri:
            st.write(t.priority.value if t.priority else "-")

st.divider()

# ---------------------------------------------------------------------------
# Build Schedule  ->  Scheduler.load_tasks_from_owner() + get_plan_for_day()
# ---------------------------------------------------------------------------
st.subheader("Build Schedule")
st.caption("Aggregates tasks across all of the owner's pets into a non-overlapping day plan.")

# Lightweight conflict check: a warning message, never a crash.
conflict_board = Scheduler(owner=owner)
conflict_board.load_tasks_from_owner()
warning = conflict_board.conflict_warning()
if warning:
    st.warning(warning + "\n\n(These will be spread apart when you generate the plan.)")
elif conflict_board.tasks:
    st.success("No scheduling conflicts detected across the owner's pets.")

if st.button("Generate schedule"):
    # Scheduler pulls every task across the owner's pets, then plans the day.
    scheduler = Scheduler(owner=owner)
    scheduler.load_tasks_from_owner()
    if not scheduler.tasks:
        st.info("No tasks across any pet yet. Add some above first.")
    else:
        today = date.today()
        plan = scheduler.get_plan_for_day(today)

        tasks_by_id = {t.task_id: t for t in scheduler.tasks}
        pets_by_id = {p.pet_id: p for p in owner.get_pets()}
        st.success(f"✅ {len(plan)} task(s) scheduled for {today.isoformat()}")
        st.table(
            [
                {
                    "Time": (
                        f"{slot.start_time.strftime('%H:%M')}"
                        f"–{slot.end_time.strftime('%H:%M')}"
                    ),
                    "Task": tasks_by_id[slot.task_id].name,
                    "Pet": (
                        pets_by_id[tasks_by_id[slot.task_id].assigned_pet_id].name
                        if tasks_by_id[slot.task_id].assigned_pet_id in pets_by_id
                        else "?"
                    ),
                    "Priority": (
                        tasks_by_id[slot.task_id].priority.value.capitalize()
                        if tasks_by_id[slot.task_id].priority
                        else "-"
                    ),
                }
                for slot in plan
            ]
        )
