# Clinic Appointment Flask App

Generated Flask API and website for the DTS114 Software Component.

## Purpose

This prototype supports appointment administration only. It does not provide diagnosis, treatment advice, prescriptions, or real patient-record storage.

## Local Setup

```bash
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Service health check |
| POST | `/api/appointments` | Create pending appointment request |
| GET | `/api/appointments` | List appointment requests |
| GET | `/api/appointments/<id>` | Get one appointment |
| PATCH | `/api/appointments/<id>/review` | Confirm or cancel request |
| GET | `/api/appointments/<id>/summary` | Non-diagnostic summary |
| GET | `/api/meta/requirements` | Generated requirements metadata |

## Example Request

```bash
curl -X POST http://127.0.0.1:5000/api/appointments ^
  -H "Content-Type: application/json" ^
  -d "{\"patient_name\":\"Alex Chen\",\"preferred_date\":\"2026-06-05\",\"preferred_time\":\"09:30\",\"appointment_type\":\"General consultation booking\"}"
```

## Tests

```bash
python -m pytest
```

## Deployment

The app includes `render.yaml`. After pushing to GitHub, connect the repository to Render or create a Blueprint from the YAML file.
