"""Streamlit interface backed entirely by PawPal+ domain objects."""
from datetime import date, datetime
import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title='PawPal+', page_icon='🐾', layout='centered')
if 'owner' not in st.session_state:
    st.session_state.owner = Owner('Jordan')
owner = st.session_state.owner
scheduler = Scheduler(owner)
st.title('🐾 PawPal+')
st.caption('Keep every pet’s care in one clear schedule.')
st.caption('Data stays during this browser session. Closing the session can clear it.')
if 'notice' in st.session_state:
    st.success(st.session_state.pop('notice'))

with st.expander('Owner profile'):
    with st.form('profile'):
        name = st.text_input('Owner name', value=owner.name)
        if st.form_submit_button('Save owner'):
            if name.strip():
                owner.name = name.strip()
                st.success('Owner updated.')
            else:
                st.error('Enter an owner name.')

with st.form('add_pet', clear_on_submit=True):
    st.subheader('Add a pet')
    pet_name = st.text_input('Pet name')
    species = st.selectbox('Species', ['dog', 'cat', 'other'])
    if st.form_submit_button('Add pet'):
        try:
            owner.add_pet(Pet(pet_name, species))
            st.session_state.notice = 'Pet added.'
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))

if not owner.pets:
    st.info('Add your first pet to start scheduling care.')
    st.stop()

st.caption('Your pets: ' + ', '.join(f'{p.name} ({p.species})' for p in owner.pets))
with st.form('add_task', clear_on_submit=True):
    st.subheader('Schedule care')
    selected_pet = st.selectbox('Pet', [p.name for p in owner.pets])
    description = st.text_input('Task description')
    due = st.date_input('Due date', value=date.today())
    clock = st.time_input('Time')
    duration = st.number_input('Duration (minutes)', min_value=1, max_value=240, value=15)
    priority = st.selectbox('Priority', ['low', 'medium', 'high'], index=1)
    frequency = st.selectbox('Frequency', ['once', 'daily', 'weekly'])
    if st.form_submit_button('Add task'):
        try:
            pet = next(p for p in owner.pets if p.name == selected_pet)
            pet.add_task(Task(description, clock.strftime('%H:%M'), due, frequency,
                              duration_minutes=int(duration), priority=priority))
            st.session_state.notice = 'Task scheduled.'
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))

st.subheader('Daily schedule')
display_date = st.date_input('Schedule date', value=date.today())
pet_filter = st.selectbox('Filter pet', ['All pets'] + [p.name for p in owner.pets])
status_filter = st.selectbox('Status', ['All', 'Pending', 'Completed'])
completed = {'All': None, 'Pending': False, 'Completed': True}[status_filter]
rows = scheduler.filter_tasks(None if pet_filter == 'All pets' else pet_filter,
                              completed, display_date)
for warning in scheduler.detect_conflicts(display_date):
    st.warning('Time conflict: ' + warning)
if not rows:
    st.info('No tasks match these filters.')
for pet, task in rows:
    left, right = st.columns([4, 1])
    with left:
        st.write(f'**{task.time} · {pet.name} · {task.description}**')
        st.caption(f'{task.duration_minutes} min · {task.priority} priority · {task.frequency} · '
                   + ('Completed' if task.completed else 'Pending'))
    with right:
        if not task.completed and st.button('Complete', key='complete_' + task.id):
            upcoming = scheduler.mark_task_complete(task.id)
            message = 'Task completed.'
            if upcoming:
                message += f' Next occurrence: {upcoming.due_date} at {upcoming.time}.'
            st.session_state.notice = message
            st.rerun()

with st.expander('Edit a pending task'):
    pending = scheduler.filter_tasks(completed=False)
    if pending:
        choices = {t.id: (p, t) for p, t in pending}
        edit_id = st.selectbox('Task to edit', list(choices),
                               format_func=lambda key: f'{choices[key][0].name}: {choices[key][1].description} ({choices[key][1].due_date})')
        pet, current = choices[edit_id]
        with st.form('edit_' + edit_id):
            title = st.text_input('Updated description', value=current.description)
            new_date = st.date_input('Updated date', value=current.due_date)
            new_time = st.time_input('Updated time', value=datetime.strptime(current.time, '%H:%M').time())
            new_duration = st.number_input('Updated duration', min_value=1, value=current.duration_minutes)
            new_priority = st.selectbox('Updated priority', ['low', 'medium', 'high'], index=['low', 'medium', 'high'].index(current.priority))
            new_frequency = st.selectbox('Updated frequency', ['once', 'daily', 'weekly'], index=['once', 'daily', 'weekly'].index(current.frequency))
            if st.form_submit_button('Save task changes'):
                try:
                    updated = Task(title, new_time.strftime('%H:%M'), new_date, new_frequency,
                                   duration_minutes=int(new_duration), priority=new_priority, id=current.id)
                    pet.tasks[pet.tasks.index(current)] = updated
                    st.session_state.notice = 'Task updated.'
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
    else:
        st.info('No pending tasks to edit.')

st.subheader('Plan within your available time')
budget = st.number_input('Available minutes', min_value=0, max_value=1440, value=60)
chosen, skipped = scheduler.build_plan(display_date, int(budget))
st.caption('Selects high priority first, then medium and low; displays chosen tasks by time. '
           'This is a suggested workload, not a conflict-free timetable.')
if chosen:
    st.table([{'Time': t.time, 'Pet': p.name, 'Task': t.description,
               'Minutes': t.duration_minutes, 'Priority': t.priority} for p, t in chosen])
else:
    st.info('No pending tasks fit this time budget.')
if skipped:
    st.write('Deferred because of the time budget: ' + ', '.join(t.description for _, t in skipped))
