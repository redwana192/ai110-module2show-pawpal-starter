from pathlib import Path
from datetime import date, time
from streamlit.testing.v1 import AppTest
from pawpal_system import Owner, Pet, Task

APP = Path(__file__).resolve().parents[1] / 'app.py'


def widget(at, kind, label):
    return next(w for w in getattr(at, kind) if w.label == label)


def populated():
    owner = Owner('Jordan')
    pet = Pet('Mochi', 'cat')
    owner.add_pet(pet)
    pet.add_task(Task('Breakfast', '08:00', date.today(), 'daily'))
    at = AppTest.from_file(str(APP), default_timeout=30)
    at.session_state['owner'] = owner
    return at.run()


def test_empty_app_and_add_pet_persists():
    at = AppTest.from_file(str(APP), default_timeout=30).run()
    assert not at.exception
    widget(at, 'text_input', 'Pet name').set_value('Biscuit')
    widget(at, 'button', 'Add pet').click().run()
    assert not at.exception
    assert at.session_state['owner'].pets[0].name == 'Biscuit'
    at.run()
    assert len(at.session_state['owner'].pets) == 1


def test_invalid_pet_shows_error():
    at = AppTest.from_file(str(APP), default_timeout=30).run()
    widget(at, 'button', 'Add pet').click().run()
    assert not at.exception
    assert any('cannot be empty' in x.value for x in at.error)


def test_add_task_and_conflict_warning():
    at = populated()
    widget(at, 'text_input', 'Task description').set_value('Medication')
    widget(at, 'time_input', 'Time').set_value(time(8, 0))
    widget(at, 'button', 'Add task').click().run()
    assert not at.exception
    assert len(at.session_state['owner'].pets[0].tasks) == 2
    assert any('Time conflict' in w.value for w in at.warning)


def test_complete_recurring_and_filter():
    at = populated()
    widget(at, 'button', 'Complete').click().run()
    assert not at.exception
    tasks = at.session_state['owner'].pets[0].tasks
    assert len(tasks) == 2 and tasks[0].completed
    widget(at, 'selectbox', 'Status').select('Completed').run()
    assert not at.exception
    assert not any(b.label == 'Complete' for b in at.button)


def test_edit_task():
    at = populated()
    widget(at, 'text_input', 'Updated description').set_value('Dinner')
    widget(at, 'number_input', 'Updated duration').set_value(25)
    widget(at, 'button', 'Save task changes').click().run()
    assert not at.exception
    task = at.session_state['owner'].pets[0].tasks[0]
    assert task.description == 'Dinner' and task.duration_minutes == 25
