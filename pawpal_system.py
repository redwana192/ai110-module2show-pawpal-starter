"""PawPal+ design skeleton: implementation follows in later commits."""
from dataclasses import dataclass, field
from datetime import date

@dataclass
class Task:
    description: str
    time: str
    due_date: date
    frequency: str = 'once'
    completed: bool = False
    duration_minutes: int = 15
    priority: str = 'medium'

    def mark_complete(self):
        """Mark this occurrence complete."""
        raise NotImplementedError

@dataclass
class Pet:
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task):
        """Attach a care task to this pet."""
        raise NotImplementedError

@dataclass
class Owner:
    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet):
        """Register a pet."""
        raise NotImplementedError

    def all_tasks(self):
        """Return pet-task pairs across the household."""
        raise NotImplementedError

class Scheduler:
    def __init__(self, owner):
        """Use the owner's existing pets and tasks."""
        self.owner = owner

    def sort_by_time(self, tasks=None):
        """Return tasks ordered by date and time."""
        raise NotImplementedError
