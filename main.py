"""CLI demo script for PawPal+ — verifies backend logic in the terminal."""

from datetime import date
from pawpal_system import Owner, Pet, Scheduler, Task


def print_section(title: str) -> None:
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print("=" * 50)


def main() -> None:
    today = date.today()

    # ── Setup owner and pets ──────────────────────────────────────────────────
    owner = Owner("Jordan")

    biscuit = Pet(name="Biscuit", species="dog", breed="Golden Retriever")
    mochi = Pet(name="Mochi", species="cat", breed="Domestic Shorthair")

    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    # ── Add tasks (intentionally out of time order) ───────────────────────────
    biscuit.add_task(Task(
        title="Evening walk",
        time="18:00",
        duration_minutes=30,
        priority="high",
        frequency="daily",
        pet_name="Biscuit",
        due_date=today,
    ))
    biscuit.add_task(Task(
        title="Morning walk",
        time="08:00",
        duration_minutes=30,
        priority="high",
        frequency="daily",
        pet_name="Biscuit",
        due_date=today,
    ))
    biscuit.add_task(Task(
        title="Breakfast feeding",
        time="09:00",
        duration_minutes=10,
        priority="high",
        frequency="daily",
        pet_name="Biscuit",
        due_date=today,
    ))
    biscuit.add_task(Task(
        title="Heartworm medication",
        time="08:00",  # same time as Morning walk — will trigger conflict!
        duration_minutes=5,
        priority="medium",
        frequency="monthly",
        pet_name="Biscuit",
        due_date=today,
    ))

    mochi.add_task(Task(
        title="Litter box cleaning",
        time="07:30",
        duration_minutes=10,
        priority="high",
        frequency="daily",
        pet_name="Mochi",
        due_date=today,
    ))
    mochi.add_task(Task(
        title="Playtime",
        time="19:00",
        duration_minutes=20,
        priority="medium",
        frequency="daily",
        pet_name="Mochi",
        due_date=today,
    ))

    scheduler = Scheduler(owner)

    # ── Today's schedule (sorted) ─────────────────────────────────────────────
    print_section("Today's Schedule")
    schedule = scheduler.get_todays_schedule()
    for task in schedule:
        print(f"  {task}")

    # ── Conflict detection ────────────────────────────────────────────────────
    print_section("Conflict Detection")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("  No conflicts detected.")

    # ── Filter: incomplete tasks for Biscuit ─────────────────────────────────
    print_section("Biscuit's Tasks (Sorted)")
    biscuit_tasks = scheduler.sort_by_time(scheduler.filter_by_pet("Biscuit"))
    for task in biscuit_tasks:
        print(f"  {task}")

    # ── Mark a task complete and verify recurrence ────────────────────────────
    print_section("Mark 'Morning walk' Complete → Check Recurrence")
    next_task = scheduler.mark_task_complete("Biscuit", "Morning walk")
    if next_task:
        print(f"  Recurring task created: {next_task.title} on {next_task.due_date}")
    else:
        print("  No recurrence generated.")

    # ── Incomplete vs completed ───────────────────────────────────────────────
    print_section("Incomplete Tasks After Completion")
    incomplete = scheduler.filter_by_status(completed=False)
    sorted_incomplete = scheduler.sort_by_time(incomplete)
    for task in sorted_incomplete:
        print(f"  {task}")

    print()


if __name__ == "__main__":
    main()
