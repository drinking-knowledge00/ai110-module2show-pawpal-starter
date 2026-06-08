"""PawPal+ Streamlit UI — connects to pawpal_system backend."""

import streamlit as st
from datetime import date
from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ── Session state initialisation ──────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_scheduler() -> Scheduler:
    return st.session_state.scheduler


def priority_icon(priority: str) -> str:
    return {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")


def freq_label(frequency: str) -> str:
    return {"daily": "Daily", "weekly": "Weekly", "once": "One-time",
            "monthly": "Monthly"}.get(frequency, frequency)


# ── Header ────────────────────────────────────────────────────────────────────
st.title("🐾 PawPal+")
st.caption("Smart pet care management — powered by Python classes & scheduling logic.")
st.divider()

# ── Step 1: Owner setup ───────────────────────────────────────────────────────
st.subheader("1. Owner Setup")
with st.form("owner_form"):
    owner_name = st.text_input("Your name", value="Jordan")
    submitted_owner = st.form_submit_button("Set Owner")

if submitted_owner and owner_name.strip():
    st.session_state.owner = Owner(owner_name.strip())
    st.session_state.scheduler = Scheduler(st.session_state.owner)
    st.success(f"Welcome, {owner_name}!")

if st.session_state.owner is None:
    st.info("Enter your name above to get started.")
    st.stop()

owner: Owner = st.session_state.owner
scheduler: Scheduler = get_scheduler()

# ── Step 2: Add a pet ─────────────────────────────────────────────────────────
st.divider()
st.subheader("2. Add a Pet")
with st.form("pet_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name", value="Biscuit")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "bird", "rabbit", "other"])
    with col3:
        breed = st.text_input("Breed (optional)", value="")
    submitted_pet = st.form_submit_button("Add Pet")

if submitted_pet and pet_name.strip():
    if owner.get_pet(pet_name.strip()) is not None:
        st.warning(f"A pet named '{pet_name}' already exists.")
    else:
        owner.add_pet(Pet(name=pet_name.strip(), species=species, breed=breed.strip()))
        st.success(f"Added {pet_name} the {species}!")

if owner.pets:
    st.write("**Your pets:**", ", ".join(f"{p.name} ({p.species})" for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

# ── Step 3: Schedule a task ───────────────────────────────────────────────────
st.divider()
st.subheader("3. Schedule a Task")

if not owner.pets:
    st.info("Add a pet first before scheduling tasks.")
else:
    with st.form("task_form"):
        pet_options = [p.name for p in owner.pets]
        col1, col2 = st.columns(2)
        with col1:
            selected_pet = st.selectbox("For which pet?", pet_options)
            task_title = st.text_input("Task title", value="Morning walk")
            task_time = st.text_input("Time (HH:MM)", value="08:00")
            task_due = st.date_input("Due date", value=date.today())
        with col2:
            task_duration = st.number_input("Duration (min)", min_value=1, max_value=480, value=30)
            task_priority = st.selectbox("Priority", ["high", "medium", "low"])
            task_frequency = st.selectbox("Frequency", ["daily", "weekly", "once", "monthly"])
            task_desc = st.text_input("Notes (optional)", value="")

        submitted_task = st.form_submit_button("Add Task")

    if submitted_task:
        # Basic time format validation
        parts = task_time.split(":")
        if len(parts) != 2 or not all(p.isdigit() for p in parts):
            st.error("Time must be in HH:MM format (e.g. 08:00).")
        else:
            pet = owner.get_pet(selected_pet)
            new_task = Task(
                title=task_title.strip(),
                time=task_time.strip(),
                duration_minutes=int(task_duration),
                priority=task_priority,
                frequency=task_frequency,
                pet_name=selected_pet,
                description=task_desc.strip(),
                due_date=task_due,
            )
            pet.add_task(new_task)
            st.success(f"Task '{task_title}' added for {selected_pet}.")

# ── Step 4: View schedule ─────────────────────────────────────────────────────
st.divider()
st.subheader("4. Today's Schedule")

if not owner.pets:
    st.info("No pets added yet.")
else:
    # Conflict detection
    all_tasks = owner.get_all_tasks()
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            st.warning(warning)

    # Filter controls
    col1, col2 = st.columns(2)
    with col1:
        pet_filter = st.selectbox(
            "Filter by pet",
            ["All pets"] + [p.name for p in owner.pets],
            key="filter_pet",
        )
    with col2:
        status_filter = st.selectbox(
            "Filter by status",
            ["All", "Incomplete", "Completed"],
            key="filter_status",
        )

    # Build filtered task list
    if pet_filter == "All pets":
        tasks = owner.get_all_tasks()
    else:
        tasks = scheduler.filter_by_pet(pet_filter)

    if status_filter == "Incomplete":
        tasks = [t for t in tasks if not t.completed]
    elif status_filter == "Completed":
        tasks = [t for t in tasks if t.completed]

    tasks = scheduler.sort_by_time(tasks)

    if not tasks:
        st.info("No tasks match the current filter.")
    else:
        for task in tasks:
            status_icon = "✅" if task.completed else "⬜"
            col_a, col_b = st.columns([6, 2])
            with col_a:
                label = (
                    f"{status_icon} **{task.time}** — {task.title} "
                    f"({task.duration_minutes} min) "
                    f"{priority_icon(task.priority)} {freq_label(task.frequency)}"
                )
                st.markdown(label)
                if task.description:
                    st.caption(task.description)
            with col_b:
                if not task.completed:
                    btn_key = f"complete_{task.pet_name}_{task.title}_{task.time}"
                    if st.button("Mark done", key=btn_key):
                        next_task = scheduler.mark_task_complete(task.pet_name, task.title)
                        if next_task:
                            st.success(
                                f"Done! Next '{task.title}' scheduled for {next_task.due_date}."
                            )
                        else:
                            st.success("Task marked complete.")
                        st.rerun()

# ── Step 5: Generate full schedule view ───────────────────────────────────────
st.divider()
st.subheader("5. Generate Today's Plan")
st.caption("Shows only today's incomplete tasks, sorted by time, with conflict warnings.")

if st.button("Generate Schedule"):
    schedule = scheduler.get_todays_schedule()
    conflicts = scheduler.detect_conflicts(schedule)

    if conflicts:
        st.subheader("⚠️ Conflicts Detected")
        for warning in conflicts:
            st.warning(warning)

    if not schedule:
        st.info("No tasks scheduled for today, or all tasks are complete!")
    else:
        st.success(f"Today's plan for {owner.name} — {len(schedule)} task(s):")
        rows = []
        for task in schedule:
            rows.append({
                "Time": task.time,
                "Pet": task.pet_name,
                "Task": task.title,
                "Duration": f"{task.duration_minutes} min",
                "Priority": f"{priority_icon(task.priority)} {task.priority}",
                "Frequency": freq_label(task.frequency),
            })
        st.table(rows)
