## Requirements Summary

### Business Problem
Clinic staff need a safe appointment administration prototype that separates patient booking from doctor/admin review, lets patients choose a date, doctor, and available slot, keeps one shared SQLite workflow, and records testing, CI/CD, Docker, deployment, and AI generation evidence.

### Scope
Appointment administration prototype only. No diagnosis, treatment advice, prescriptions, or real patient records.

### Actors
- Patient: Registers, logs in, books appointments, cancels own requests, reschedules pending requests.
- Doctor: Reviews own queue, manages own profile, views day-board, audit events.
- Admin Staff: Manages all queues, doctors, accounts.
- Clinic System: Handles authentication, scheduling, persistence.

### Functional Requirements
1. Sign In with demo accounts (patient, doctor, admin) and Sign Up for new accounts.
2. Patient dashboard: date selection, doctor roster, slot picker, appointment creation, search, cancellation, reschedule.
3. Doctor dashboard: linked queue, day-board, profile management, audit, review modal.
4. Admin dashboard: all queues, doctor management.
5. Scheduling: future weekdays, 30-min slots, doctor shifts, capacity, appointment types.
6. Reschedule: patient-owned pending requests, doctor/admin with notes.
7. Audit trail per appointment.
8. Non-diagnostic summary per appointment.
9. Metadata endpoint for requirements.
10. Safety validation rejecting forbidden terms.

### Non-Functional Requirements
- SQLite runtime persistence with auto schema creation.
- Role-based access control.
- APIFREE-generated clinic image and doctor photos.
- Pytest tests, Docker, GitHub Actions CI, Render deployment.
- AI-DLC traceability in artefacts.

### AI-DLC Traceability
- DeepSeek-generated requirements, user stories, validation checklist, UML diagrams.
- DeepSeek generation metadata in artifacts/deepseek_generation_metadata.json.
- APIFREE image metadata in artifacts/apifree_image_generation_metadata.json.
- APIFREE doctor photo metadata in artifacts/doctor_photo_generation_metadata.json.
- Release metadata in artifacts/release_metadata.json.
