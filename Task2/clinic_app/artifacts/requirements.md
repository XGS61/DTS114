# Clinic Appointment Administration Requirements

## Business Problem

A small clinic needs a safe appointment administration prototype that can collect appointment requests, flag time-slot conflicts, and keep receptionist human review before any appointment is confirmed.

## Methodology

The project uses an AI-DLC-informed iterative methodology:

- Inception: define clinic problem, actors, requirements, and safety boundary.
- Construction: generate requirements, UML, Flask API, website, image, and validation checklist.
- Operations: use Git, tests, CI/CD, and deployment evidence.

## Scope

In scope:

- Appointment request collection.
- Appointment list and status display.
- Conflict flag for same date/time requests.
- Receptionist review with confirm/cancel decision.
- Non-diagnostic administrative summary.

Out of scope:

- Diagnosis.
- Treatment advice.
- Prescriptions.
- Real patient records.
- Production clinic scheduling.

## Actors

- Patient: submits an appointment request.
- Receptionist: reviews, confirms, or cancels requests.
- Clinic System: validates requests, flags conflicts, stores prototype records, and exposes API responses.

## Functional Requirements

1. The website shall display a clinic appointment request form.
2. The system shall create new requests with `Pending Review` status.
3. The system shall flag conflicts when a new request uses a date/time already used by an active request.
4. The receptionist shall be able to confirm or cancel an appointment request.
5. The system shall provide a non-diagnostic administrative summary for each request.
6. The system shall expose JSON API endpoints for appointment creation, listing, review, summary, and project metadata.
7. The website shall display a generated clinic image.

## Non-Functional Requirements

1. The project shall be runnable locally with Python and Flask.
2. The project shall include tests for core API behaviour.
3. The project shall include a GitHub Actions CI workflow.
4. The project shall include deployment-ready Render configuration.
5. The project shall avoid hard-coded API keys and real patient data.

## Safety Requirements

1. The application shall state that it is a prototype.
2. The application shall reject obvious diagnosis/treatment-advice requests.
3. The administrative summary shall explicitly state that it is non-diagnostic.
4. Appointment confirmation shall require human receptionist review.
