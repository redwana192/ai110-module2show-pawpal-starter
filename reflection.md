# PawPal+ Project Reflection

Draft for Redwan to review after running the project. Edit statements to match your own understanding and experience.

## 1. System Design

### Three core user actions
1. Add a pet to an owner's household.
2. Schedule or edit a care task, such as feeding or a walk.
3. View the day's tasks and mark them complete.

### 1a. Initial design
The design uses four classes. Owner manages pets. Pet stores its tasks. Task stores the description, due date, time, duration, priority, frequency, and completion state. Scheduler reads tasks through Owner and organizes them. The draft UML and initial skeleton show these responsibilities.

### 1b. Design changes
The final design adds a unique ID for each task and puts household completion in Scheduler.mark_task_complete(). Task.mark_complete() creates the next occurrence, and Scheduler attaches it to the correct pet. This keeps the model independent of Streamlit and prevents repeated completion from creating duplicate tasks. The final UML includes the additional methods.

## 2. Scheduling Logic and Tradeoffs

### 2a. Constraints and priorities
The scheduler considers date, start time, completion state, duration, and priority. The daily view sorts by time. The time-budget plan considers high-priority tasks first, then medium and low, selecting tasks that fit the remaining minutes. The selected tasks are displayed chronologically. Tasks that do not fit are listed as deferred.

### 2b. Tradeoffs
Conflict detection checks identical dates and start times, including tasks for different pets. It does not detect overlapping durations or travel time. This keeps the basic rule easy to understand, but a later version should check intervals. The budget plan is greedy, so it does not promise the best possible combination. It also does not resolve conflicts automatically.

## 3. AI Collaboration

### 3a. How AI was used
ChatGPT prepared the design, class skeleton, implementation, tests, and documentation using file editing and terminal commands. CLI output and automated tests were used to check the work. This was one conversation, rather than separate chats for each phase. Separating design, implementation, and testing into distinct steps helped keep the work organized. The student still needs to run the package locally and review these explanations.

### 3b. Judgment and verification
The implementation avoids letting UI button handlers independently create recurring tasks. Instead, the Scheduler controls completion and attachment of the next occurrence. Tests check that a second completion does not create another copy. This was an implementation decision made during the AI-assisted build; it should not be described as a suggestion personally rejected by the student unless that occurred during review.

## 4. Testing and Verification

### 4a. What was tested
The 29 tests cover task addition and completion, sorting, combined filters, daily and weekly recurrence, year rollover, duplicate completion, conflicts, empty households, priority budgets, invalid inputs, and UI actions. Streamlit AppTest checks adding a pet, session persistence, adding a task, warnings, editing, and completing a recurring task.

### 4b. Confidence
Provisional confidence: 4/5 based on passing automated tests in the preparation environment. The student's Windows setup and manual walkthrough still need checking. More testing could cover browser accessibility, many pets, and long-term storage. The app uses session memory and does not save data permanently.

## 5. Reflection

### 5a. What went well
The CLI and browser interface use the same backend. That makes the scheduling rules easier to test independently.

### 5b. What could improve
Add persistent storage, overlapping-duration detection, and clearer reminders for overdue care. Recurrence currently advances from the original due date, so a late task may generate another overdue occurrence.

### 5c. Key takeaway
AI can prepare a lot of code quickly, but the person responsible for the project needs to understand the design, verify behavior, and accurately describe what they reviewed.
