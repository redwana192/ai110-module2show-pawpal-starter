# AI Assistance Record

## Tool and context
ChatGPT/Codex, one conversation. The user supplied the Week 4 CodePath requirements and Canvas check-in. No Claude, VS Code agent sessions, or multi-model comparisons are claimed.

## Design
- Task: prepare Owner, Pet, Task, and Scheduler with a Mermaid blueprint and dataclass skeleton.
- Result: diagrams/uml_draft.mmd and an initial skeleton commit.
- Design review: Scheduler references Owner rather than maintaining a second list of pets/tasks.

## Implementation
- Task: implement CLI-first logic, sorting, filtering, recurrence, conflicts, priority time budgets, and Streamlit integration.
- Files: pawpal_system.py, main.py, app.py, diagrams/uml_final.mmd.
- Decisions: normalize times to HH:MM; compare dates separately; make repeated completion idempotent; keep recurrence attachment in Scheduler.
- A complex optimization engine was not implemented. A simple greedy budget selector is documented as a tradeoff, not an optimal planner.

## Verification
- Files: tests/test_pawpal.py and tests/test_app.py.
- Commands: python main.py; python -m pytest.
- Result: 29 tests passed in the preparation environment, including five Streamlit AppTest scenarios.
- Actual output is stored in evidence/ and copied into README.md.

## Limitations and student review
The starter repository and instructions were inspected through web retrieval. Direct GitHub cloning was unavailable in the preparation environment, so the package contains a standalone local Git history. The student must create their CodePath fork and connect it before pushing. No remote push or submission has occurred. The student should run the tests, try the UI, review the reflection, and add their own observations. No fabricated prompts or personal review claims are included.
