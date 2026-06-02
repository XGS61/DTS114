| # | Check | Evidence |
|---|-------|----------|
| 1 | DeepSeek API generated SDLC artefacts and metadata records generation status | artifacts/deepseek_generation_metadata.json |
| 2 | Requirements, user stories, and acceptance criteria are generated and reviewed | artifacts/generated_requirements.md; artifacts/generated_user_stories.json |
| 3 | UML source reflects patient, doctor/admin, shared data, and review workflow | artifacts/diagrams/*.puml |
| 4 | Login supports demo Patient, Doctor, and Admin roles | tests/test_app.py |
| 5 | Patient can create appointment requests and view own statuses | tests/test_app.py |
| 6 | Staff can view shared queue and confirm/cancel appointments | tests/test_app.py |
| 7 | Conflict detection flags active appointments with same date/time | tests/test_app.py |
| 8 | Safety validation rejects diagnosis, treatment, or prescription wording | tests/test_app.py |
| 9 | Summary endpoint is non-diagnostic: GET /api/appointments/<id>/summary | tests/test_app.py |
| 10 | Meta requirements endpoint exposes AI-DLC and DeepSeek tooling rationale | tests/test_app.py |
| 11 | Custom English date picker avoids localised browser date text | tests/test_app.py |
| 12 | GitHub Actions CI is configured to run pytest | .github/workflows/ci.yml |
| 13 | Render deployment configuration is present | render.yaml |
| 14 | Screenshot guide explains commit, deployment, and CI/CD evidence | Task2/screenshots/README.md |
