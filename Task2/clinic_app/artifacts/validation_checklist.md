# Validation Checklist

| Check | Evidence |
|---|---|
| Single Task 1 notebook exists | `Task1/clinic_appointment_generator.ipynb` |
| Generated Flask project exists | `Task2/clinic_app` |
| Website displays generated image | `static/generated_clinic_image.png` |
| Login supports patient, doctor, and admin roles | `/login`, `/api/auth/login` |
| Patient and staff dashboards are separate | `/patient`, `/staff` |
| Appointment data is shared | `data/appointments.json` runtime store |
| Human review boundary exists | `Pending Review`, `Confirmed`, `Cancelled` |
| Review action requires staff role | `PATCH /api/appointments/<id>/review` |
| Safety boundary blocks diagnosis/treatment requests | appointment payload validation |
| Summary is non-diagnostic | `GET /api/appointments/<id>/summary` |
| Optional API keys are not committed | `.env.example`, `.gitignore` |
| Tests pass | `python -m pytest` |
| CI/CD configuration exists | `.github/workflows/ci.yml` |
| Deployment configuration exists | `render.yaml` |
| Git evidence exists | meaningful commit history on `main` |
