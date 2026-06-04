# Deployment and Evidence Guide

## GitHub Repository

Repository URL:

https://github.com/XGS61/DTS114

Latest CI evidence should be captured from the GitHub Actions page after pushing the final commit.

Primary Docker deployed website URL:

https://dts114-clinic-appointment-generator-g8md.onrender.com/

Primary Docker app login URL:

https://dts114-clinic-appointment-generator-g8md.onrender.com/app/login

Fallback native Python Render deployment:

https://dts114-clinic-appointment-generator.onrender.com/login

Primary Docker health check URL:

https://dts114-clinic-appointment-generator-g8md.onrender.com/health

Fallback native Python Render health check:

https://dts114-clinic-appointment-generator.onrender.com/health

## Render Docker Deployment Steps

1. Log in to Render.
2. Create a new Blueprint from the root-level `render.yaml`, or create a new Web Service from the GitHub repository.
3. Confirm Docker runtime is selected.
4. Confirm the service uses:
   - Root directory: `Task2/clinic_app`
   - Dockerfile path: `./Dockerfile`
   - Docker context: `.`
   - Health check path: `/health`
5. After deployment, open the deployed `/` page and `/health` endpoint.

## Local Docker Verification

```bash
cd Task2/clinic_app
docker build -t dts114-clinic-app .
docker run --rm -p 5000:5000 -e FLASK_SECRET_KEY=local-docker-secret dts114-clinic-app
```

The local container URL is `http://127.0.0.1:5000/`. This proves the Docker image works on the marking machine. Render uses the same Dockerfile to build and run the container in the cloud, then provides the public website URL.

## Conda Environment Setup

For local Python and notebook execution, create the environment from the repository root:

```bash
conda env create -f environment.yml
conda activate dts114-clinic-generator
```

Use this environment for running the Task 1 notebook, `python scripts/validate_submission.py`, and `python -m pytest`.

## Native Render Fallback

The project also keeps `runtime.txt` for a native Python fallback. Use this fallback only if Docker service creation is blocked:

- Root directory: `Task2/clinic_app`
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Python runtime: `python-3.11.9`

## Required Screenshot Evidence

Place the final screenshots in `Task2/screenshots/`:

| Filename | Required evidence |
|---|---|
| `01_commit_records.png` | GitHub commit history showing meaningful commits |
| `02_deployed_website.png` | Render Docker deployed website, preferably the public login page with generated image |
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
