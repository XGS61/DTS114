# Clinic Appointment System Generator - Validation Checklist

| # | Check | Evidence |
|---|-------|----------|
| 1 | Task 1 contains exactly one generator notebook | Task1/clinic_appointment_generator.ipynb; scripts/validate_submission.py |
| 2 | Notebook can generate Flask API, role-based website, SDLC artefacts, generated image, tests, CI/CD, Docker, Render config, and release metadata | Task1/clinic_appointment_generator.ipynb |
| 3 | DeepSeek API generated SDLC artefacts and metadata records generation status | artifacts/deepseek_generation_metadata.json |
| 4 | APIFREE API generated the clinic image and fictional doctor photos when configured, with reproducible fallback metadata | artifacts/apifree_image_generation_metadata.json; artifacts/doctor_photo_generation_metadata.json; static/generated_clinic_image.png; static/doctors/*.png |
| 5 | Requirements, user stories, acceptance criteria, and release metadata are generated and reviewed | artifacts/generated_requirements.md; artifacts/generated_user_stories.json; artifacts/release_metadata.json |
| 6 | UML source reflects patient booking, doctor-only review, admin oversight, doctor schedule, slot selection, reschedule flow, SQLite storage, and audit trail | artifacts/diagrams/*.puml |
| 7 | Login supports demo Patient, Doctor, and Admin roles with hashed credential checks | tests/test_app.py |
| 8 | Self-registration creates prototype Patient, Doctor, and Admin accounts with hashed credential checks | tests/test_app.py |
| 9 | Doctor registration creates a linked doctor profile and routes to the staff dashboard | tests/test_app.py |
| 10 | Doctor accounts see only their linked appointment queue, audit events, and day-board slots | tests/test_app.py |
| 11 | Doctor accounts can update their own department, room, focus, shift, capacity, and profile note | tests/test_app.py |
| 12 | Admin accounts can see all queues and create doctor accounts/profiles visible to patients | tests/test_app.py |
| 13 | Patient can create, search, view, cancel own requests, and reschedule own Pending Review requests only | tests/test_app.py |
| 14 | Scheduling validation enforces future weekdays, selected doctor shifts, clinic hours, slot increments, capacity, and allowed appointment types | tests/test_app.py |
| 15 | Doctor-specific availability endpoint reports available, occupied, capacity, and conflicting slots | tests/test_app.py |
| 16 | Selected-date doctor roster and today's doctor roster endpoints return fictional doctors and generated photo paths | tests/test_app.py |
| 17 | Conflict detection flags active duplicate doctor slots and recalculates after cancellation or reschedule | tests/test_app.py |
| 18 | Audit events are created after create, review, cancel, reschedule, and conflict changes | tests/test_app.py |
| 19 | Safety validation rejects diagnosis, treatment, prescription, or medical-advice wording | tests/test_app.py |
| 20 | Summary endpoint remains non-diagnostic and administrative only | tests/test_app.py |
| 21 | Custom English date picker avoids localised browser date text | tests/test_app.py |
| 22 | Submission validation checks structure, metadata, English-only files, and secret leakage | scripts/validate_submission.py |
| 23 | GitHub Actions CI runs validation, syntax check, pytest, Docker build, and Docker smoke test | .github/workflows/ci.yml |
| 24 | Dockerfile, Render config, environment.yml, and README explain local and cloud execution | Task2/clinic_app/Dockerfile; render.yaml; environment.yml; README.md |
| 25 | Screenshot guide explains commit, deployment, and CI/CD evidence | Task2/screenshots/README.md |
