"""A deterministic CLI demonstration; no Streamlit dependency."""
from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    """Demonstrate sorting, filters, budgets, conflicts, and recurrence."""
    day = date(2026, 11, 1)
    owner = Owner('Jordan')
    dog, cat = Pet('Biscuit', 'dog'), Pet('Mochi', 'cat')
    owner.add_pet(dog)
    owner.add_pet(cat)
    dog.add_task(Task('Evening walk', '18:00', day, duration_minutes=30, priority='low'))
    dog.add_task(Task('Morning walk', '08:00', day, 'daily', duration_minutes=20, priority='high'))
    cat.add_task(Task('Breakfast', '08:00', day, 'daily', duration_minutes=10, priority='high'))
    cat.add_task(Task('Grooming', '12:00', day, 'weekly', duration_minutes=15))
    scheduler = Scheduler(owner)
    print("Today's Schedule (2026-11-01)")
    for pet, task in scheduler.filter_tasks(on_date=day):
        print(f'{task.time} | {pet.name:7} | {task.description:13} | {task.duration_minutes:2} min | {task.priority}')
    print('\nConflict warnings:')
    for warning in scheduler.detect_conflicts(day):
        print('WARNING:', warning)
    print('\nPending tasks for Mochi:', len(scheduler.filter_tasks(pet_name='Mochi', completed=False)))
    selected, skipped = scheduler.build_plan(day, 30)
    print('30-minute plan:', ', '.join(task.description for _, task in selected))
    print('Deferred:', ', '.join(task.description for _, task in skipped))
    next_task = scheduler.mark_task_complete(dog.tasks[1].id, completed_on=day)
    print(f'Completed Morning walk; next occurrence: {next_task.due_date} {next_task.time}')
    print('Completed tasks:', len(scheduler.filter_tasks(completed=True)))


if __name__ == '__main__':
    main()
