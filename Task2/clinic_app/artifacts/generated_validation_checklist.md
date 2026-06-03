| # | Check | Evidence |
|---|-------|----------|
| 1 | DeepSeek API generated SDLC artefacts and metadata records generation status | artifacts/deepseek_generation_metadata.json |
| 2 | APIFREE API generated the clinic image when configured, with reproducible fallback metadata | artifacts/apifree_image_generation_metadata.json; static/generated_clinic_image.png |
| 3 | Requirements, user stories, and acceptance criteria are generated and reviewed | artifacts/generated_requirements.md; artifacts/generated_user_stories.json |
| 4 | UML source reflects patient, doctor/admin, shared data, and review workflow | artifacts/diagrams/*.puml |
| 5 | Login supports demo Patient, Doctor, and Admin roles | tests/test_app.py |
| 6 | Appointment APIs require login before create/list/summary operations | tests/test_app.py |
| 7 | Patient can create appointment requests and view own statuses only | tests/test_app.py |
| 8 | Staff can view shared queue and confirm/cancel appointments | tests/test_app.py |
| 9 | Conflict detection flags all active appointments with same date/time and recalculates after cancellation | tests/test_app.py |
| 10 | Safety validation rejects diagnosis, treatment, or prescription wording | tests/test_app.py |
| 11 | Summary endpoint is non-diagnostic: GET /api/appointments/<id>/summary | tests/test_app.py |
| 12 | Meta requirements endpoint exposes AI-DLC, DeepSeek, and APIFREE tooling rationale | tests/test_app.py |
| 13 | Custom English date picker avoids localised browser date text | tests/test_app.py |
| 14 | Submission validation checks structure, metadata, English-only files, and secrets | scripts/validate_submission.py |
| 15 | GitHub Actions CI runs validation, syntax check, pytest, Docker build, and Docker smoke test | .github/workflows/ci.yml |
| 16 | Dockerfile and Render deployment configuration are present | Task2/clinic_app/Dockerfile; render.yaml |
| 17 | Screenshot guide explains commit, deployment, and CI/CD evidence | Task2/screenshots/README.md |
