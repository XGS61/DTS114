# Validation Checklist

## Requirements Alignment

- [x] Requirements define actors, workflow, scope, and safety boundary.
- [x] User stories include acceptance criteria.
- [x] UML source files map to the appointment workflow.
- [x] API endpoints support the website workflow.

## Safety Boundary

- [x] No diagnosis is provided.
- [x] No treatment advice is provided.
- [x] No real patient records are required.
- [x] Human review is required before confirmation.

## API Quality

- [x] `POST /api/appointments` validates required fields.
- [x] Conflict checking marks overlapping active slots.
- [x] `PATCH /api/appointments/<id>/review` restricts status values.
- [x] Summary endpoint returns non-diagnostic wording.
- [x] Missing resources return 404 JSON responses.

## Operations Evidence

- [x] Git repository is used for local version control.
- [x] Pytest tests are included.
- [x] GitHub Actions workflow is included.
- [x] Render deployment configuration is included.

## Review Notes

This project is a coursework prototype. All generated artefacts should be reviewed by the student before final submission.
