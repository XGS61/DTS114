# Submission Checklist

Use this checklist before creating the final `StudentID-Your_Name.zip`.

## Required Structure

- [ ] Root folder is renamed from `StudentID-Your_Name` to the real student ID and name.
- [ ] `Task1/` contains exactly one notebook: `clinic_appointment_generator.ipynb`.
- [ ] `Task2/clinic_app/` contains the generated Flask API and website.
- [ ] `Task2/screenshots/` contains the three required evidence screenshots.

## Evidence

- [ ] Commit records screenshot: `Task2/screenshots/01_commit_records.png`.
- [ ] Deployed website screenshot: `Task2/screenshots/02_deployed_website.png`.
- [ ] CI/CD workflow screenshot: `Task2/screenshots/03_cicd_workflow.png`.
- [ ] GitHub Actions latest run is successful.
- [ ] Render Docker deployment loads `/login`.
- [ ] Render Docker health check loads `/health`.
- [ ] Docker image builds locally or in GitHub Actions.

## Validation Commands

Run from the repository root:

```bash
python scripts/validate_submission.py --require-screenshots
```

Run from `Task2/clinic_app`:

```bash
python -m py_compile app.py
python -m pytest
```

Optional local Docker check:

```bash
docker build -t dts114-clinic-app .
docker run --rm -p 5000:5000 dts114-clinic-app
```

## Clean Packaging

- [ ] Do not include `.env`.
- [ ] Do not include API keys.
- [ ] Do not include `.pytest_cache`.
- [ ] Do not include `__pycache__`.
- [ ] Do not include runtime `Task2/clinic_app/data/appointments.json`.
- [ ] Keep `Task2/clinic_app/data/.gitkeep`.
- [ ] Keep `Task2/clinic_app/Dockerfile` and `Task2/clinic_app/.dockerignore`.

Suggested PowerShell cleanup before zipping:

```powershell
Remove-Item -Recurse -Force Task2/clinic_app/.pytest_cache -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force Task2/clinic_app/__pycache__ -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force Task2/clinic_app/tests/__pycache__ -ErrorAction SilentlyContinue
Remove-Item -Force Task2/clinic_app/data/appointments.json -ErrorAction SilentlyContinue
```
