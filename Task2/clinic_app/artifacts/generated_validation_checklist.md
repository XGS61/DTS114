| # | Check | Evidence |
|---|-------|----------|
| 1 | DeepSeek API generated SDLC artefacts and metadata records generation status | artifacts/deepseek_generation_metadata.json |
| 2 | Requirements, user stories, and acceptance criteria are generated and reviewed | artifacts/generated_requirements.md; artifacts/generated_user_stories.json |
| 3 | UML source reflects patient, doctor/admin, shared data, and review workflow | artifacts/diagrams/*.puml |
| 4 | Login supports demo Patient, Doctor, and Admin roles | tests/test_app.py |
| 5 | Appointment APIs require login before create/list/summary operations | tests/test_app.py |
| 6 | Patient can create appointment requests and view own statuses only | tests/test_app.py |
| 7 | Staff can view shared queue and confirm/cancel appointments | tests/test_app.py |
| 8 | Conflict detection flags all active appointments with same date/time and recalculates after cancellation | tests/test_app.py |
| 9 | Safety validation rejects diagnosis, treatment, or prescription wording | tests/test_app.py |
| 10 | Summary endpoint is non-diagnostic: GET /api/appointments/<id>/summary | tests/test_app.py |
| 11 | Meta requirements endpoint exposes AI-DLC and DeepSeek tooling rationale | tests/test_app.py |
| 12 | Custom English date picker avoids localised browser date text | tests/test_app.py |
| 13 | Submission validation checks structure, metadata, English-only files, and secrets | scripts/validate_submission.py |
| 14 | GitHub Actions CI runs validation, syntax check, and pytest | .github/workflows/ci.yml |
| 15 | Render deployment configuration and Python runtime pin are present | render.yaml; Task2/clinic_app/runtime.txt |
| 16 | Screenshot guide explains commit, deployment, and CI/CD evidence | Task2/screenshots/README.md |
