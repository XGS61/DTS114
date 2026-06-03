# Clinic Appointment Flask App

Generated Flask API and website for the DTS114 Software Component.

## Purpose

This prototype supports appointment administration only. It does not provide diagnosis, treatment advice, prescriptions, or real patient-record storage.

Appointment API routes are session-protected. Use a demo account through `/login` or `POST /api/auth/login` before creating, listing, opening, or summarising appointments.

## Local Setup

```bash
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000/login`.

## Demo Accounts

| Role | Username | Password |
|---|---|---|
| Patient | `patient` | `patient123` |
| Doctor | `doctor` | `doctor123` |
| Admin | `admin` | `admin123` |

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Service health check |
| POST | `/api/auth/login` | Start a demo role session |
| POST | `/api/auth/logout` | End the current demo session |
| GET | `/api/auth/session` | Inspect the current demo session |
| POST | `/api/appointments` | Create pending appointment request |
| GET | `/api/appointments` | List visible appointment requests |
| GET | `/api/appointments/<id>` | Get one appointment |
| PATCH | `/api/appointments/<id>/review` | Staff-only review action |
| GET | `/api/appointments/<id>/summary` | Non-diagnostic summary |
| GET | `/api/meta/requirements` | Generated requirements metadata |

## Example Requests

```bash
curl -X POST http://127.0.0.1:5000/api/appointments ^
  -H "Content-Type: application/json" ^
  -d "{\"patient_name\":\"Alex Chen\",\"preferred_date\":\"2026-06-05\",\"preferred_time\":\"09:30\",\"appointment_type\":\"General consultation booking\"}"
```

## Tests

```bash
python -m py_compile app.py
python -m pytest
```

From the repository root, run the submission-level validation:

```bash
python scripts/validate_submission.py
```

## Deployment

The app includes `render.yaml`. After pushing to GitHub, connect the repository to Render or create a Blueprint from the YAML file. Configure only required environment variables in Render.

The app also includes `runtime.txt` to pin the Render Python runtime to Python 3.11 for stable dependency installation.
