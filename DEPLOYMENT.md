# Deployment and Evidence Guide

## GitHub Repository

Repository URL:

https://github.com/XGS61/DTS114

Latest CI evidence should be captured from the GitHub Actions page after pushing the final commit.

Deployed website URL:

https://dts114-clinic-appointment-generator.onrender.com/login

Health check URL:

https://dts114-clinic-appointment-generator.onrender.com/health

## Render Deployment Steps

1. Log in to Render.
2. Create a new Blueprint or Web Service from the GitHub repository.
3. Use the root-level `render.yaml`.
4. Confirm the service uses:
   - Root directory: `Task2/clinic_app`
   - Python runtime: `python-3.11.9` from `Task2/clinic_app/runtime.txt`
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
   - Health check path: `/health`
5. After deployment, open the deployed `/login` page and `/health` endpoint.

## Required Screenshot Evidence

Place the final screenshots in `Task2/screenshots/`:

| Filename | Required evidence |
|---|---|
| `01_commit_records.png` | GitHub commit history showing meaningful commits |
| `02_deployed_website.png` | Render deployed website, preferably the login page with generated image |
| `03_cicd_workflow.png` | GitHub Actions workflow run showing success |

## Final Packaging Check

Before creating the final zip, run:

```bash
python scripts/validate_submission.py --require-screenshots
```

The command should pass only after the three evidence screenshots exist.

## Local Verification Commands

```bash
cd Task2/clinic_app
python -m py_compile app.py
python -m pytest
```

The current test suite verifies API health, login, appointment creation, role access control, conflict recalculation, non-diagnostic summaries, AI tooling metadata, and the custom English date picker.
