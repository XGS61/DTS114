# Generated Requirements: Clinic Appointment System

## Business Problem

Clinic staff need a safe prototype that separates patient appointment booking from doctor/admin review while keeping one shared appointment workflow.

## Scope

The system supports appointment administration only. It must not provide diagnosis, treatment advice, prescriptions, or storage of real patient records.

## Actors

- Patient: submits appointment requests and tracks status.
- Doctor: reviews appointment requests and confirms or cancels bookings.
- Admin Staff: manages the shared appointment queue.
- Clinic System: stores appointment data, flags conflicts, and produces non-diagnostic summaries.

## Functional Requirements

| ID | Requirement |
|---|---|
| FR-01 | The system shall provide a demo login screen with patient, doctor, and admin roles. |
| FR-02 | The system shall route patients to a patient booking dashboard. |
| FR-03 | The system shall route doctor/admin users to a staff review dashboard. |
| FR-04 | The patient dashboard shall create appointment requests with patient name, date, time, type, and administrative reason. |
| FR-05 | Appointment API routes shall require an authenticated demo session. |
| FR-06 | Patient users shall see only appointments created by their account. |
| FR-07 | New appointment requests shall start with `Pending Review` status. |
| FR-08 | The shared backend shall store appointment requests in a JSON data file for prototype persistence. |
| FR-09 | The system shall recalculate conflict flags when active appointments share or stop sharing the same date and time. |
| FR-10 | Doctor/admin users shall confirm, cancel, or reopen appointment requests. |
| FR-11 | The system shall provide a non-diagnostic administrative summary for each visible request. |
| FR-12 | The system shall expose REST-style API endpoints for health, authentication, appointments, review, summary, and metadata. |
| FR-13 | The website shall display a generated clinic appointment image. |
| FR-14 | The system shall avoid irrelevant external APIs unless they directly support the appointment administration workflow. |

## Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-01 | All user-visible text shall be in English. |
| NFR-02 | API keys shall be read from environment variables and must not be committed. |
| NFR-03 | The application shall include automated tests for core API behaviour. |
| NFR-04 | The repository shall include GitHub Actions CI configuration for validation, syntax checking, pytest, Docker image build, and Docker smoke testing. |
| NFR-05 | The repository shall include Dockerfile and Render Docker deployment configuration. |
| NFR-06 | The project shall provide clear Git commit history for coursework evidence. |
| NFR-07 | The repository shall include submission validation for structure, DeepSeek metadata, English-only files, and possible API key leakage. |

## AI-DLC Traceability

- Inception: define clinic problem, roles, user stories, acceptance criteria, and safety boundary.
- Construction: generate requirements, UML, Flask code, website files, image, tests, and validation checklist.
- Operations: use Git commits, CI/CD, Docker containerisation, Render deployment configuration, and screenshot evidence.

## Safety Controls

- Reject requests containing diagnosis or treatment wording.
- Keep summaries non-diagnostic.
- Require doctor/admin permission for review actions.
- Use deterministic fallback when optional AI generation is unavailable.
