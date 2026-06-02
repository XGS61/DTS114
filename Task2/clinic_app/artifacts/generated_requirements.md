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
2. Patient can create appointment requests; view own request status.
3. Staff (doctor/admin) can view shared queue of pending appointments.
4. Staff can confirm or cancel appointments (human review).
5. Conflict detection: flag when active appointments share same date and time.
6. Status values: Pending Review, Confirmed, Cancelled.
7. Staff-only review endpoint.
8. Non-diagnostic summary endpoint: GET /api/appointments/<id>/summary.
9. Metadata endpoint: GET /api/meta/requirements.
10. Safety validation: reject diagnosis/treatment/prescription wording.

## Non-Functional Requirements
- Automated tests in tests/test_app.py.
- CI with GitHub Actions.
- Deployment via Render.
- LLM-backed generation evidence in artifacts/deepseek_generation_metadata.json.

## AI-DLC Traceability
The requirements were generated using an AI-DLC-informed iterative methodology. Outputs include user stories, validation checklist, UML diagrams, Flask API, tests, CI, and deployment config.
