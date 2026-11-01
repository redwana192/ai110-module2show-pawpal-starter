"""UI-independent pet care objects and scheduling algorithms."""
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta
from uuid import uuid4


def clean_text(value, label):
    """Require a nonempty text value."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{label} cannot be empty.')
    return value.strip()


@dataclass
class Task:
    description: str
    time: str
    due_date: date
    frequency: str = 'once'
    completed: bool = False
    duration_minutes: int = 15
    priority: str = 'medium'
    id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self):
        """Validate and normalize task data at creation."""
        self.description = clean_text(self.description, 'Description')
        if not isinstance(self.time, str):
            raise ValueError('Time must use HH:MM.')
        try:
            parsed = datetime.strptime(self.time, '%H:%M')
        except ValueError as exc:
            raise ValueError('Time must use HH:MM (00:00–23:59).') from exc
        self.time = parsed.strftime('%H:%M')
        if type(self.due_date) is not date:
            raise ValueError('A due date is required.')
        if self.frequency not in ('once', 'daily', 'weekly'):
            raise ValueError('Frequency must be once, daily, or weekly.')
        if self.priority not in ('low', 'medium', 'high'):
            raise ValueError('Priority must be low, medium, or high.')
        if type(self.duration_minutes) is not int or self.duration_minutes <= 0:
            raise ValueError('Duration must be a positive whole number.')

    def mark_complete(self):
        """Complete this occurrence once and return its next occurrence, if any."""
        if self.completed:
            return None
        self.completed = True
        days = {'daily': 1, 'weekly': 7}.get(self.frequency)
        if days is None:
            return None
        return replace(self, due_date=self.due_date + timedelta(days=days),
                       completed=False, id=uuid4().hex)


@dataclass
class Pet:
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self):
        """Validate the pet's name and species."""
        self.name = clean_text(self.name, 'Pet name')
        self.species = clean_text(self.species, 'Species')

    def add_task(self, task):
        """Attach a task, rejecting duplicate IDs."""
        if any(existing.id == task.id for existing in self.tasks):
            raise ValueError('This task is already attached to the pet.')
        self.tasks.append(task)


@dataclass
class Owner:
    name: str
    pets: list[Pet] = field(default_factory=list)

    def __post_init__(self):
        """Validate the owner's name."""
        self.name = clean_text(self.name, 'Owner name')

    def add_pet(self, pet):
        """Register a pet with a household-unique name."""
        if any(p.name.casefold() == pet.name.casefold() for p in self.pets):
            raise ValueError('A pet with that name already exists.')
        self.pets.append(pet)

    def all_tasks(self):
        """Return pet-task pairs without copying the task objects."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


class Scheduler:
    def __init__(self, owner):
        """Reference the owner's single source of household data."""
        self.owner = owner

    def sort_by_time(self, tasks=None):
        """Sort pet-task pairs chronologically without mutating storage."""
        pairs = self.owner.all_tasks() if tasks is None else tasks
        return sorted(pairs, key=lambda pair: (pair[1].due_date, pair[1].time))

    def filter_tasks(self, pet_name=None, completed=None, on_date=None):
        """Filter by any combination of pet, completion state, and date."""
        return self.sort_by_time([
            (pet, task) for pet, task in self.owner.all_tasks()
            if (pet_name is None or pet.name.casefold() == pet_name.casefold())
            and (completed is None or task.completed == completed)
            and (on_date is None or task.due_date == on_date)
        ])

    def mark_task_complete(self, task_id):
        """Complete an owned task and attach its next recurring occurrence."""
        for pet, task in self.owner.all_tasks():
            if task.id == task_id:
                next_task = task.mark_complete()
                if next_task is not None:
                    pet.add_task(next_task)
                return next_task
        raise ValueError('Task not found.')

    def detect_conflicts(self, on_date=None):
        """Warn about identical start dates/times for any pending tasks."""
        slots = {}
        for pet, task in self.filter_tasks(completed=False, on_date=on_date):
            slots.setdefault((task.due_date, task.time), []).append(
                f'{pet.name}: {task.description}')
        return [f'{day.isoformat()} {clock} — ' + '; '.join(labels)
                for (day, clock), labels in slots.items() if len(labels) > 1]

    def build_plan(self, on_date, available_minutes):
        """Greedily select pending tasks by priority within a time budget."""
        if type(available_minutes) is not int or available_minutes < 0:
            raise ValueError('Available minutes must be a nonnegative integer.')
        rank = {'high': 0, 'medium': 1, 'low': 2}
        candidates = sorted(self.filter_tasks(completed=False, on_date=on_date),
                            key=lambda pair: (rank[pair[1].priority], pair[1].time))
        chosen, skipped = [], []
        remaining = available_minutes
        for pair in candidates:
            if pair[1].duration_minutes <= remaining:
                chosen.append(pair)
                remaining -= pair[1].duration_minutes
            else:
                skipped.append(pair)
        return self.sort_by_time(chosen), skipped
