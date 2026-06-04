# Clinic Appointment System Generator - Requirements

This file mirrors the generated requirements artefact for marker convenience.

# Clinic Appointment System Generator - Requirements Summary

## Generator Variant
- Variant id: general-clinic
- Display name: Clinic Appointment System
- Domain focus: general clinic appointment administration

## Business Problem
Clinic staff need a safe appointment administration prototype that separates patient booking from doctor/admin review, lets patients choose a date, doctor, and available slot, keeps one shared SQLite workflow, and records testing, CI/CD, Docker, deployment, and AI generation evidence.

## Scope
Appointment administration prototype only. No diagnosis, treatment advice, prescriptions, or real patient records.

## Configured Appointment Types
- General consultation booking
- Vaccination appointment booking
- Follow-up appointment booking
- Administrative query booking

## Configured Fictional Doctor Schedule
- Dr Amelia Hart | General Medicine | 09:00-12:30 | Consulting Room 2A
- Dr Noah Bennett | Preventive Care | 10:00-15:00 | Consulting Room 3B
- Dr Priya Raman | Follow-up Coordination | 13:00-17:00 | Consulting Room 1C

## Functional Requirements
1. Users can log in with hashed demo credentials or self-register a prototype patient, doctor, or admin account.
2. Registration validates username, display name, role, password length, duplicate usernames, and password confirmation.
3. Doctor registration creates a linked fictional doctor profile so patient booking and staff scheduling can immediately use the new doctor.
4. Patient dashboard lets the patient select a future weekday, choose a fictional on-duty doctor, view doctor-specific available slots, create an appointment request, search own requests, track status, cancel own request, and request a pending appointment reschedule.
5. Doctor dashboard shows only appointments, audit events, and day-board slots linked to that doctor's profile.
6. Doctor dashboard lets the doctor maintain their visible department, room, appointment focus, status, weekday shift, slot length, capacity, and profile note.
7. Admin dashboard shows all appointment queues and can create doctor accounts with matching patient-visible doctor profiles.
8. Authentication APIs support registration, login, logout, and session inspection with role-based redirects.
9. Appointment APIs require an authenticated session and enforce patient, doctor, and admin visibility boundaries.
10. Scheduling validation enforces future weekdays, selected doctor's shift, slot increments, capacity, and allowed appointment types.
11. Conflict detection is recalculated on overlapping doctor/date/time slots against doctor capacity.
12. Safety validation rejects diagnosis, treatment, prescription, and medical-advice wording.
13. DeepSeek/APIFREE metadata, tests, Docker, GitHub Actions CI, Render config, and release metadata support coursework evidence.

## AI-DLC Traceability
- DeepSeek-supported: requirements, user stories, validation checklist, and UML source.
- APIFREE-supported: clinic interface image and fictional doctor roster photos.
- Deterministic fallback keeps the generated app reproducible when API keys are unavailable.
