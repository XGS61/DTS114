# Clinic Appointment System Generator - Requirements

## Business Problem
Clinic staff need a safe prototype that separates patient appointment booking from doctor/admin review while keeping one shared appointment workflow.

## Scope
Appointment administration prototype only. No diagnosis, treatment advice, prescriptions, or real patient records.

## Actors
- Patient: Requests appointments; views own request status.
- Doctor: Reviews and confirms/cancels appointments.
- Admin Staff: Reviews and confirms/cancels appointments.
- Clinic System: Manages appointment store, conflict detection, safety validation.

## Functional Requirements
1. Login with demo accounts (patient, doctor, admin).
2. Appointment APIs require an authenticated demo session.
3. Patient can create appointment requests and view own request status only.
4. Staff (doctor/admin) can view the shared queue of appointment requests.
5. Staff can confirm or cancel appointments (human review).
6. Conflict detection recalculates flags when active appointments share or stop sharing the same date and time.
7. Status values: Pending Review, Confirmed, Cancelled.
8. Staff-only review endpoint: PATCH /api/appointments/<id>/review.
9. Non-diagnostic summary endpoint: GET /api/appointments/<id>/summary.
10. Metadata endpoint: GET /api/meta/requirements.
11. Safety validation: reject diagnosis/treatment/prescription wording.

## Non-Functional Requirements
- Automated tests in tests/test_app.py.
- CI with GitHub Actions, including submission validation, syntax check, pytest, Docker image build, and Docker smoke test.
- Containerisation via Dockerfile and cloud deployment via Render Docker runtime.
- LLM-backed generation evidence in artifacts/deepseek_generation_metadata.json.
- Submission validation checks one-notebook structure, DeepSeek metadata, English-only files, and possible API key leakage.

## AI-DLC Traceability
The requirements were generated using an AI-DLC-informed iterative methodology. Outputs include user stories, validation checklist, UML diagrams, Flask API, tests, CI, and deployment config.
