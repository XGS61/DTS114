# DTS114 Clinic Appointment Generator

This coursework software component implements an AI-DLC-informed generator for a Flask-based clinic appointment administration prototype.

The project demonstrates:

- SDLC artefact generation: requirements, user stories, acceptance criteria, UML source, and validation checklist.
- A generated Flask API and role-based website for clinic appointment administration.
- A generated website image shown in the front end.
- Separate patient and doctor/admin dashboards using one shared appointment data store.
- Human review boundary: appointments are created as `Pending Review` and require staff confirmation or cancellation.
- Safety boundary: no diagnosis, no treatment advice, no prescriptions, and no real patient records.
- DeepSeek API support for Task 1 artefact generation when configured; committed artefacts record the latest generated run in `Task2/clinic_app/artifacts/deepseek_generation_metadata.json`.
- APIFREE API support for Task 1 clinic image generation when configured; committed artefacts record the image generation run in `Task2/clinic_app/artifacts/apifree_image_generation_metadata.json`.
- Testing, Docker containerisation, CI/CD workflow, and deployment-ready Render configuration.
- Submission validation for structure, DeepSeek metadata, APIFREE metadata, English-only files, and secret scanning.

## Task 1 Generator Synchronisation

`Task1/clinic_appointment_generator.ipynb` is the single generator notebook for this submission. Running the full notebook from the repository root or from the `Task1` folder regenerates the Task 2 Flask project, including:

- Flask API and website files in `Task2/clinic_app`.
- Requirements, user stories, validation checklist, and UML source files.
- Generated clinic image at `Task2/clinic_app/static/generated_clinic_image.png`.
- DeepSeek and APIFREE metadata files in `Task2/clinic_app/artifacts`.
- Tests, Dockerfile, Render configuration, CI workflow, screenshot guide, and documentation.

Optional API calls are controlled by environment variables. If DeepSeek or APIFREE keys are unavailable, the notebook uses deterministic fallback artefacts so the generated application remains runnable.

## Structure

```text
StudentID-Your_Name/
  environment.yml
  Task1/
    clinic_appointment_generator.ipynb
  Task2/
    clinic_app/
      app.py
      Dockerfile
      requirements.txt
      render.yaml
      templates/
      static/
      tests/
      artifacts/
      data/
    screenshots/
  .github/workflows/
```

## Run Locally

### Conda Environment

Create the coursework environment from the repository root:

```bash
conda env create -f environment.yml
conda activate dts114-clinic-generator
```

This environment supports the Task 1 notebook, the Task 2 Flask app, and the pytest validation commands.

### Flask App

```bash
cd Task2/clinic_app
python -m pip install -r requirements.txt
python app.py
```

Open:

- Login: http://127.0.0.1:5000/
- App login: http://127.0.0.1:5000/app/login
- Patient dashboard: http://127.0.0.1:5000/app/patient
- Staff dashboard: http://127.0.0.1:5000/app/staff
- Health check: http://127.0.0.1:5000/health

## Demo Accounts

| Role | Username | Password | Purpose |
|---|---|---|---|
| Patient | `patient` | `patient123` | Submit and track appointment requests |
| Doctor | `doctor` | `doctor123` | Review, confirm, cancel, and summarise requests |
| Admin | `admin` | `admin123` | Review and manage the shared queue |

## Optional Environment Variables

Copy `.env.example` to `.env` for local testing, but do not commit `.env`.

| Variable | Purpose |
|---|---|
| `FLASK_SECRET_KEY` | Session signing key for Flask |
| `DEEPSEEK_API_KEY` | Notebook support for DeepSeek SDLC artefact generation |
| `ENABLE_LLM_GENERATION` | Set to `1` only when intentionally testing optional LLM generation |
| `APIFREE_API_KEY` | Notebook support for APIFREE clinic image generation |
| `ENABLE_IMAGE_API_GENERATION` | Set to `1` only when intentionally testing optional image API generation |
| `APIFREE_IMAGE_MODEL` | Optional APIFREE image model override; default is `qwen/qwen-image-2512` |
| `APIFREE_API_BASE` | Optional APIFREE base URL override |

## Test

```bash
cd Task2/clinic_app
python -m py_compile app.py
python -m pytest
```

Run the coursework structure validation from the repository root:

```bash
python scripts/validate_submission.py
```

Before final packaging, add the three required screenshots and run:

```bash
python scripts/validate_submission.py --require-screenshots
```

## Docker

The generated app can be run as a local container for Week 5 containerisation evidence:

```bash
cd Task2/clinic_app
docker build -t dts114-clinic-app .
docker run --rm -p 5000:5000 dts114-clinic-app
```

Open `http://127.0.0.1:5000/`. In cloud deployment, Render builds and runs the same Dockerfile as a public web service. Local Docker proves the container works on the marking machine; Render Docker deployment proves the same container can run as an online website.
 
## GitHub / Deployment Evidence

The `Task2/screenshots` folder explains the three required screenshots:

1. Git commit records.
2. Deployed website.
3. CI/CD workflow.

After creating an empty GitHub repository in the required account, add it as a remote and push:

```bash
git remote add origin <your-github-repository-url>
git branch -M main
git push -u origin main
```

## AI Use and Academic Integrity

This software includes generated artefact templates, optional API hooks, and deterministic generation logic to support learning. Final report and presentation wording should be written in the student's own words, with AI use acknowledged according to the module policy.

Supporting documents:

- `AI_USE.md`
- `REFERENCES.md`
- `DEPLOYMENT.md`
- `SUBMISSION_CHECKLIST.md`
