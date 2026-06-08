"""Automated tests for PawPal+ core behaviors."""

from datetime import date, timedelta
import pytest
from pawpal_system import Owner, Pet, Scheduler, Task


# ── helpers ───────────────────────────────────────────────────────────────────

def make_task(title="Walk", time="09:00", pet_name="Rex", frequency="once",
              priority="medium", days_offset=0) -> Task:
    return Task(
        title=title,
        time=time,
        duration_minutes=20,
        priority=priority,
        frequency=frequency,
        pet_name=pet_name,
        due_date=date.today() + timedelta(days=days_offset),
    )


def make_owner_with_pet(pet_name="Rex") -> tuple[Owner, Pet, Scheduler]:
    owner = Owner("Jordan")
    pet = Pet(name=pet_name, species="dog")
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    return owner, pet, scheduler


# ── Task: mark_complete ───────────────────────────────────────────────────────

def test_mark_complete_changes_status():
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_mark_complete_once_returns_none():
    task = make_task(frequency="once")
    result = task.mark_complete()
    assert result is None


def test_mark_complete_daily_returns_next_day():
    task = make_task(frequency="daily")
    original_due = task.due_date
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == original_due + timedelta(days=1)
    assert next_task.completed is False


def test_mark_complete_weekly_returns_next_week():
    task = make_task(frequency="weekly")
    original_due = task.due_date
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == original_due + timedelta(weeks=1)


# ── Pet: add_task / remove_task ───────────────────────────────────────────────

def test_add_task_increases_count():
    pet = Pet(name="Rex", species="dog")
    assert len(pet.tasks) == 0
    pet.add_task(make_task())
    assert len(pet.tasks) == 1
    pet.add_task(make_task(title="Feed"))
    assert len(pet.tasks) == 2


def test_remove_task_decreases_count():
    pet = Pet(name="Rex", species="dog")
    pet.add_task(make_task(title="Walk"))
    assert len(pet.tasks) == 1
    removed = pet.remove_task("Walk")
    assert removed is True
    assert len(pet.tasks) == 0


def test_remove_task_nonexistent_returns_false():
    pet = Pet(name="Rex", species="dog")
    assert pet.remove_task("Ghost task") is False


# ── Scheduler: sort_by_time ───────────────────────────────────────────────────

def test_sort_by_time_returns_chronological_order():
    owner, pet, scheduler = make_owner_with_pet()
    pet.add_task(make_task(title="C", time="18:00"))
    pet.add_task(make_task(title="A", time="07:30"))
    pet.add_task(make_task(title="B", time="12:00"))
    sorted_tasks = scheduler.sort_by_time()
    times = [t.time for t in sorted_tasks]
    assert times == sorted(times)


def test_sort_empty_list_returns_empty():
    owner, pet, scheduler = make_owner_with_pet()
    assert scheduler.sort_by_time() == []


# ── Scheduler: filter_by_pet ──────────────────────────────────────────────────

def test_filter_by_pet_returns_only_matching_tasks():
    owner = Owner("Jordan")
    rex = Pet(name="Rex", species="dog")
    mochi = Pet(name="Mochi", species="cat")
    owner.add_pet(rex)
    owner.add_pet(mochi)
    rex.add_task(make_task(title="Walk Rex", pet_name="Rex"))
    mochi.add_task(make_task(title="Feed Mochi", pet_name="Mochi"))
    scheduler = Scheduler(owner)
    rex_tasks = scheduler.filter_by_pet("Rex")
    assert len(rex_tasks) == 1
    assert rex_tasks[0].title == "Walk Rex"


# ── Scheduler: filter_by_status ───────────────────────────────────────────────

def test_filter_by_status_incomplete():
    owner, pet, scheduler = make_owner_with_pet()
    t1 = make_task(title="A")
    t2 = make_task(title="B")
    t2.completed = True
    pet.add_task(t1)
    pet.add_task(t2)
    incomplete = scheduler.filter_by_status(completed=False)
    assert all(not t.completed for t in incomplete)
    assert len(incomplete) == 1


# ── Scheduler: detect_conflicts ───────────────────────────────────────────────

def test_detect_conflicts_same_time():
    owner, pet, scheduler = make_owner_with_pet()
    pet.add_task(make_task(title="Walk", time="08:00"))
    pet.add_task(make_task(title="Meds", time="08:00"))
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]


def test_detect_conflicts_no_conflict():
    owner, pet, scheduler = make_owner_with_pet()
    pet.add_task(make_task(title="Walk", time="08:00"))
    pet.add_task(make_task(title="Meds", time="09:00"))
    conflicts = scheduler.detect_conflicts()
    assert conflicts == []


# ── Scheduler: mark_task_complete + recurrence ────────────────────────────────

def test_mark_task_complete_creates_recurring_task():
    owner, pet, scheduler = make_owner_with_pet(pet_name="Rex")
    pet.add_task(make_task(title="Walk", frequency="daily", pet_name="Rex"))
    initial_count = len(pet.tasks)
    scheduler.mark_task_complete("Rex", "Walk")
    assert len(pet.tasks) == initial_count + 1
    new_tasks = [t for t in pet.tasks if not t.completed]
    assert new_tasks[0].due_date == date.today() + timedelta(days=1)


def test_mark_task_complete_once_does_not_create_new_task():
    owner, pet, scheduler = make_owner_with_pet(pet_name="Rex")
    pet.add_task(make_task(title="Vet", frequency="once", pet_name="Rex"))
    initial_count = len(pet.tasks)
    result = scheduler.mark_task_complete("Rex", "Vet")
    assert result is None
    assert len(pet.tasks) == initial_count  # no new task added


# ── Scheduler: get_todays_schedule ────────────────────────────────────────────

def test_get_todays_schedule_excludes_other_days():
    owner, pet, scheduler = make_owner_with_pet()
    pet.add_task(make_task(title="Today task", time="09:00", days_offset=0))
    pet.add_task(make_task(title="Tomorrow task", time="09:00", days_offset=1))
    schedule = scheduler.get_todays_schedule()
    assert len(schedule) == 1
    assert schedule[0].title == "Today task"


def test_get_todays_schedule_excludes_completed():
    owner, pet, scheduler = make_owner_with_pet()
    t = make_task(title="Done task", time="08:00")
    t.completed = True
    pet.add_task(t)
    pet.add_task(make_task(title="Pending task", time="09:00"))
    schedule = scheduler.get_todays_schedule()
    assert all(not t.completed for t in schedule)
