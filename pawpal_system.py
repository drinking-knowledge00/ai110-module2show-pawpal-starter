"""PawPal+ backend: Task, Pet, Owner, and Scheduler classes."""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


@dataclass
class Task:
    """A single pet care activity."""
    title: str
    time: str  # "HH:MM"
    duration_minutes: int
    priority: str  # "low" | "medium" | "high"
    frequency: str  # "once" | "daily" | "weekly"
    pet_name: str
    description: str = ""
    completed: bool = False
    due_date: date = field(default_factory=date.today)

    def mark_complete(self) -> Optional["Task"]:
        """Mark task done; return a new Task for the next occurrence if recurring."""
        self.completed = True
        if self.frequency == "daily":
            return Task(
                title=self.title,
                time=self.time,
                duration_minutes=self.duration_minutes,
                priority=self.priority,
                frequency=self.frequency,
                pet_name=self.pet_name,
                description=self.description,
                due_date=self.due_date + timedelta(days=1),
            )
        if self.frequency == "weekly":
            return Task(
                title=self.title,
                time=self.time,
                duration_minutes=self.duration_minutes,
                priority=self.priority,
                frequency=self.frequency,
                pet_name=self.pet_name,
                description=self.description,
                due_date=self.due_date + timedelta(weeks=1),
            )
        return None

    def __str__(self) -> str:
        status = "✓" if self.completed else "○"
        return (
            f"[{status}] {self.time} — {self.title} ({self.duration_minutes} min)"
            f" [priority: {self.priority}] [freq: {self.frequency}]"
        )


@dataclass
class Pet:
    """A pet owned by an Owner, holding that pet's task list."""
    name: str
    species: str
    breed: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> bool:
        """Remove the first task matching the given title; return True if found."""
        for i, t in enumerate(self.tasks):
            if t.title == title:
                self.tasks.pop(i)
                return True
        return False

    def get_tasks(self) -> list[Task]:
        """Return all tasks belonging to this pet."""
        return list(self.tasks)


class Owner:
    """An owner managing one or more pets."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_pet(self, name: str) -> Optional[Pet]:
        """Return the pet with the given name, or None."""
        for pet in self.pets:
            if pet.name.lower() == name.lower():
                return pet
        return None

    def get_all_tasks(self) -> list[Task]:
        """Collect every task from every pet into one flat list."""
        tasks: list[Task] = []
        for pet in self.pets:
            tasks.extend(pet.get_tasks())
        return tasks


class Scheduler:
    """Retrieves, sorts, filters, and validates tasks for an Owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    # ── sorting ──────────────────────────────────────────────────────────────

    def sort_by_time(self, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Return tasks sorted chronologically by HH:MM time string."""
        source = tasks if tasks is not None else self.owner.get_all_tasks()
        return sorted(source, key=lambda t: t.time)

    # ── filtering ────────────────────────────────────────────────────────────

    def filter_by_pet(self, pet_name: str) -> list[Task]:
        """Return all tasks whose pet_name matches (case-insensitive)."""
        return [t for t in self.owner.get_all_tasks()
                if t.pet_name.lower() == pet_name.lower()]

    def filter_by_status(self, completed: bool) -> list[Task]:
        """Return tasks filtered by completion status."""
        return [t for t in self.owner.get_all_tasks()
                if t.completed == completed]

    def filter_by_priority(self, priority: str) -> list[Task]:
        """Return tasks that match the given priority level."""
        return [t for t in self.owner.get_all_tasks()
                if t.priority.lower() == priority.lower()]

    # ── conflict detection ────────────────────────────────────────────────────

    def detect_conflicts(self, tasks: Optional[list[Task]] = None) -> list[str]:
        """Return warning messages for any two tasks sharing the exact same time."""
        source = tasks if tasks is not None else self.owner.get_all_tasks()
        seen: dict[str, Task] = {}
        warnings: list[str] = []
        for task in source:
            key = task.time
            if key in seen:
                other = seen[key]
                warnings.append(
                    f"⚠ Conflict at {task.time}: '{task.title}' (for {task.pet_name})"
                    f" overlaps with '{other.title}' (for {other.pet_name})"
                )
            else:
                seen[key] = task
        return warnings

    # ── schedule generation ───────────────────────────────────────────────────

    def get_todays_schedule(self) -> list[Task]:
        """Return today's incomplete tasks sorted by time."""
        today = date.today()
        todays = [t for t in self.owner.get_all_tasks()
                  if t.due_date == today and not t.completed]
        return self.sort_by_time(todays)

    # ── task completion + recurrence ──────────────────────────────────────────

    def mark_task_complete(self, pet_name: str, task_title: str) -> Optional[Task]:
        """Mark a task done and, if recurring, add the next occurrence to the pet."""
        pet = self.owner.get_pet(pet_name)
        if pet is None:
            return None
        for task in pet.tasks:
            if task.title == task_title and not task.completed:
                next_task = task.mark_complete()
                if next_task is not None:
                    pet.add_task(next_task)
                return next_task
        return None