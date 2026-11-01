from datetime import date, timedelta
import pytest
from pawpal_system import Owner, Pet, Task, Scheduler

DAY = date(2026, 12, 31)


def task(**kwargs):
    return Task(**({'description': 'Feed', 'time': '08:00', 'due_date': DAY} | kwargs))


def household():
    owner = Owner('Jordan')
    dog, cat = Pet('Biscuit', 'dog'), Pet('Mochi', 'cat')
    owner.add_pet(dog)
    owner.add_pet(cat)
    return owner, dog, cat, Scheduler(owner)


def test_completion_changes_status():
    t = task()
    assert t.mark_complete() is None
    assert t.completed


def test_task_addition():
    pet = Pet('Mochi', 'cat')
    t = task()
    pet.add_task(t)
    assert pet.tasks == [t]


def test_separate_pet_lists():
    _, dog, cat, _ = household()
    dog.add_task(task())
    assert cat.tasks == []


def test_sorting_numeric_normalization_and_dates():
    _, dog, _, scheduler = household()
    late, early, tomorrow = task(time='18:00'), task(time='8:00'), task(due_date=DAY+timedelta(days=1), time='00:00')
    for t in [tomorrow, late, early]:
        dog.add_task(t)
    assert [t for _, t in scheduler.sort_by_time()] == [early, late, tomorrow]
    assert dog.tasks == [tomorrow, late, early]
    assert scheduler.sort_by_time([]) == []


@pytest.mark.parametrize('frequency,days', [('daily', 1), ('weekly', 7)])
def test_recurrence_and_year_rollover(frequency, days):
    _, dog, _, scheduler = household()
    original = task(frequency=frequency, priority='high', duration_minutes=20)
    dog.add_task(original)
    upcoming = scheduler.mark_task_complete(original.id)
    assert original.completed
    assert upcoming.due_date == DAY + timedelta(days=days)
    assert not upcoming.completed and upcoming.id != original.id
    assert (upcoming.time, upcoming.priority, upcoming.duration_minutes) == ('08:00', 'high', 20)
    assert dog.tasks == [original, upcoming]
    assert scheduler.mark_task_complete(original.id) is None
    assert len(dog.tasks) == 2


def test_once_creates_no_new_task():
    _, dog, _, scheduler = household()
    t = task()
    dog.add_task(t)
    assert scheduler.mark_task_complete(t.id) is None
    assert len(dog.tasks) == 1


def test_filters_combine_and_false_is_respected():
    _, dog, cat, scheduler = household()
    dog.add_task(task())
    cat.add_task(task(completed=True))
    cat.add_task(task(due_date=DAY+timedelta(days=1)))
    assert len(scheduler.filter_tasks()) == 3
    assert len(scheduler.filter_tasks(pet_name='mochi', completed=False)) == 1
    assert len(scheduler.filter_tasks(on_date=DAY, completed=True)) == 1
    assert scheduler.filter_tasks(pet_name='missing') == []


def test_conflicts_across_pets_and_within_pet():
    _, dog, cat, scheduler = household()
    dog.add_task(task(description='Walk'))
    dog.add_task(task(description='Medication'))
    cat.add_task(task(description='Feed cat'))
    warnings = scheduler.detect_conflicts(DAY)
    assert len(warnings) == 1
    assert all(text in warnings[0] for text in ['Biscuit', 'Mochi', 'Walk', 'Medication'])


def test_conflicts_ignore_complete_and_other_dates():
    _, dog, cat, scheduler = household()
    dog.add_task(task())
    cat.add_task(task(completed=True))
    cat.add_task(task(due_date=DAY+timedelta(days=1)))
    assert scheduler.detect_conflicts(DAY) == []


def test_empty_household():
    scheduler = Scheduler(Owner('Jordan'))
    assert scheduler.sort_by_time() == []
    assert scheduler.detect_conflicts() == []
    assert scheduler.build_plan(DAY, 30) == ([], [])


def test_budget_prioritizes_high_then_displays_chronologically():
    _, dog, _, scheduler = household()
    low = task(description='Play', time='07:00', priority='low', duration_minutes=10)
    high = task(description='Medication', time='09:00', priority='high', duration_minutes=20)
    for t in (low, high):
        dog.add_task(t)
    chosen, skipped = scheduler.build_plan(DAY, 20)
    assert [t for _, t in chosen] == [high]
    assert [t for _, t in skipped] == [low]
    assert scheduler.build_plan(DAY, 0)[0] == []


@pytest.mark.parametrize('kwargs', [
    {'description': ' '}, {'time': '24:00'}, {'time': '12:60'},
    {'time': 'abc'}, {'time': None}, {'due_date': '2026-01-01'},
    {'duration_minutes': 0}, {'duration_minutes': 1.5},
    {'priority': 'urgent'}, {'frequency': 'monthly'}])
def test_invalid_task_data(kwargs):
    with pytest.raises(ValueError):
        task(**kwargs)


def test_duplicate_pet_and_task_rejected():
    owner, dog, _, _ = household()
    with pytest.raises(ValueError):
        owner.add_pet(Pet('biscuit', 'dog'))
    t = task()
    dog.add_task(t)
    with pytest.raises(ValueError):
        dog.add_task(t)


def test_unknown_task_and_invalid_budget():
    _, _, _, scheduler = household()
    with pytest.raises(ValueError):
        scheduler.mark_task_complete('missing')
    with pytest.raises(ValueError):
        scheduler.build_plan(DAY, -1)
