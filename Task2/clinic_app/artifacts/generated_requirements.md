# Generated Requirements

## Business Problem
A small clinic needs a safe appointment administration prototype that collects requests, flags slot conflicts, and keeps receptionist review before confirmation.

## Actors
Patient, Receptionist, Clinic System

## Safety Boundary
- Scope: Appointment administration only
- Not allowed: diagnosis, treatment advice, prescriptions, real patient records
- Human review: Receptionist confirms or cancels each request.

## Core Requirements
1. Create appointment requests as Pending Review.
2. Flag same date/time conflicts.
3. Allow receptionist confirmation or cancellation.
4. Return non-diagnostic administrative summaries.
5. Provide tests, CI/CD, and deployment-ready configuration.