# PawPal+

A Python and Streamlit pet-care scheduler for a household with multiple pets.
Prepared with ChatGPT assistance for the CodePath Module 2 / CEN4010 Week 4 exercise.

## Setup (Windows)
Requires Python 3.10 or newer. Open a terminal in this folder.

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
python -m pytest
python -m streamlit run app.py
```

Keep the terminal running while using the browser. Streamlit's email prompt is optional; press Enter to skip it. If the browser does not open, use http://localhost:8501.

## Features and architecture
- Add an owner and multiple pets; add and edit dated care tasks.
- Track task duration, priority, frequency, and completion.
- Sort and filter the daily schedule, warn about matching start times, and automatically create daily/weekly occurrences when completing a task.
- Build a suggested workload within an available-minute budget.
- Owner contains pets; each Pet contains Tasks; Scheduler reads through Owner.
- The backend in pawpal_system.py has no Streamlit dependency.
- The UI stores the Owner object in st.session_state for reruns within the session.
- Mermaid sources: diagrams/uml.mmd (initial design) and diagrams/uml_final.mmd (implemented design).

## Smarter Scheduling
- `Scheduler.sort_by_time()`: stable chronological ordering by date and normalized HH:MM; original storage order is unchanged.
- `Scheduler.filter_tasks()`: combine pet name, completion status, and due date; returns sorted pet-task pairs.
- `Scheduler.detect_conflicts()`: group pending tasks by exact date/start time and return warnings across all pets. Completed tasks are excluded. Complexity O(n log n) including filtering/sorting.
- `Task.mark_complete()` and `Scheduler.mark_task_complete()`: create a fresh task one or seven days after the date the task is completed, retaining its properties. Repeated completion cannot create duplicates. UI calls the Scheduler method so the new task is attached to its pet.
- `Scheduler.build_plan()`: high priority first, with time breaking ties; select tasks that fit the remaining budget, then display chronologically. Complexity O(n log n). This greedy plan does not guarantee an optimal combination or resolve overlapping times.

## Demo Walkthrough
1. Add Biscuit (dog) and Mochi (cat). Their names must be unique within the household.
2. Add a daily morning walk for Biscuit at 08:00 and daily breakfast for Mochi at 08:00 on the same date.
3. View that date's schedule. A conflict warning shows both activities. Add another task at 18:00 to see chronological ordering.
4. Filter by pet and Pending/Completed. Complete the daily walk; its current occurrence becomes completed and tomorrow's occurrence appears on tomorrow's date. Use Schedule date to find it.
5. Expand Edit a pending task, change its description or time, and save. The same task ID is retained.
6. Enter a time budget. The planner favors higher priority tasks and lists deferred tasks with a clear explanation.

## Sample Output
This is the actual deterministic CLI output from `python main.py` (fixed demo date):

```text
Today's Schedule (2026-11-01)
08:00 | Biscuit | Morning walk  | 20 min | high
08:00 | Mochi   | Breakfast     | 10 min | high
12:00 | Mochi   | Grooming      | 15 min | medium
18:00 | Biscuit | Evening walk  | 30 min | low

Conflict warnings:
WARNING: 2026-11-01 08:00 — Biscuit: Morning walk; Mochi: Breakfast

Pending tasks for Mochi: 2
30-minute plan: Morning walk, Breakfast
Deferred: Grooming, Evening walk
Completed Morning walk; next occurrence: 2026-11-02 08:00
Completed tasks: 1
```

## Testing PawPal+
Run `python -m pytest`. Backend tests cover completion, task addition, sorting, filtering, recurrence, year rollover, duplicate prevention, conflicts, invalid data, empty households, and budgets. UI tests cover pet addition, session reruns, validation, conflict warnings, completion, and editing. AppTest uses a 30-second timeout to accommodate slower computers.

Actual successful run in the preparation environment:

```text
============================= test session starts ==============================
platform linux -- Python 3.12.14, pytest-9.2.0, pluggy-1.7.0
plugins: anyio-4.14.2
collected 30 items

tests/test_app.py .....                                                  [ 16%]
tests/test_pawpal.py .........................                           [100%]

======================== 30 passed, 1 warning in 2.26s =========================
```

Confidence: **4/5 stars**. The original 29 tests passed on Windows, and the updated test suite also checks late completion.

## Limitations
- Session memory only: closing or losing the session may clear pets/tasks. No file persistence is claimed.
- Conflicts use identical starts, not overlapping durations.
- No background notifications or calendar integration.
- The date budget selects workload; it does not automatically reschedule tasks.

## Submission status
The GitHub fork is the repository to submit for the PawPal+ exercise.

Starter reference: https://github.com/codepath/ai110-module2show-pawpal-starter
