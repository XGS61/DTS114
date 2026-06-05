# Submission Checklist

Use this checklist before creating the final coursework archive. It is written as a marker-facing and student-facing guide, so each item links back to visible evidence in the project.

## Current Evidence Summary

| Area | Current status | Evidence |
|---|---|---|
| Task 1 single notebook | Ready | `Task1/clinic_appointment_generator.ipynb` |
| Task 2 generated Flask app | Ready | `Task2/clinic_app/` |
| Generated image displayed on website | Ready | `Task2/clinic_app/static/generated_clinic_image.png` |
| Generated fictional doctor photos | Ready | `Task2/clinic_app/static/doctors/` |
| SDLC artefacts and UML | Ready | `Task2/clinic_app/artifacts/` |
| DeepSeek metadata | Ready | `Task2/clinic_app/artifacts/deepseek_generation_metadata.json` |
| APIFREE metadata | Ready | `Task2/clinic_app/artifacts/apifree_image_generation_metadata.json` and `doctor_photo_generation_metadata.json` |
| Tests | Ready | `58 passed` from `python -m pytest` |
| CI/CD | Ready | GitHub Actions evidence screenshot and workflow file |
| Docker | Ready | `Task2/clinic_app/Dockerfile` |
| Online deployment | Ready | Render Docker public website and `/health` endpoint |
| Screenshot evidence | Ready | `Task2/screenshots/` |

## Required Folder Structure

Before submission, confirm this structure is preserved:

```text
StudentID-Your_Name/
  Task1/
    clinic_appointment_generator.ipynb
  Task2/
    clinic_app/
      app.py
      templates/
      static/
      tests/
      artifacts/
      Dockerfile
      requirements.txt
      render.yaml
    screenshots/
      01_commit_records.png
      02_deployed_website.png
      03_cicd_workflow.png
  .github/
    workflows/
      ci.yml
  scripts/
    validate_submission.py
  README.md
  AI_USE.md
  DEPLOYMENT.md
  SUBMISSION_CHECKLIST.md
  environment.yml
```

Checklist:

- [ ] Rename `StudentID-Your_Name` to the real student ID and name if the submission portal requires it.
- [ ] Keep exactly one notebook inside `Task1/`.
- [ ] Keep `Task2/clinic_app/` as the generated Flask website and API project.
- [ ] Keep the three real screenshots inside `Task2/screenshots/`.
- [ ] Do not include extra notebooks that could confuse the marker.

## Task 1 Regeneration Check

Task 1 should be able to regenerate Task 2 automatically. Run from the repository root:

```bash
jupyter nbconvert --to notebook --execute --inplace Task1/clinic_appointment_generator.ipynb
```

Expected result:

- `Task2/clinic_app/app.py` exists.
- Templates, static files, tests, Docker files, CI workflow, Render config, and documentation exist.
- Generated SDLC artefacts exist under `Task2/clinic_app/artifacts/`.
- `generated_clinic_image.png` exists and is displayed on the login page.
- Doctor photos exist under `Task2/clinic_app/static/doctors/`.

## Software Behaviour Check

Run from `Task2/clinic_app`:

```bash
python -m py_compile app.py
python -m pytest
```

Expected result:

- Python syntax passes.
- The pytest suite passes.
- Appointment creation, role access, availability, rescheduling, audit trail, summaries, AI metadata, English UI controls, and generated image evidence are covered.

## Submission Validation Check

Run from the repository root:

```bash
python scripts/validate_submission.py --require-screenshots
```

Expected result:

- Required files are present.
- Only one Task 1 notebook exists.
- Screenshots are present and non-empty.
- DeepSeek and APIFREE metadata exist.
- No committed API keys are detected.
- No Chinese text is detected in project-visible files.
- Required Docker, CI, deployment, and environment files exist.

## Local Python Environment

Recommended Conda environment:

```bash
conda env create -f environment.yml
conda activate dts114-clinic-generator
```

Direct app environment:

```bash
cd Task2/clinic_app
python -m pip install -r requirements.txt
python app.py
```

Open:

```text
http://127.0.0.1:5000/
```

## Local Docker Environment

Run from `Task2/clinic_app`:

```bash
docker build -t dts114-clinic-app:v1.3.1 .
docker run --rm -p 5000:5000 -e FLASK_SECRET_KEY=local-docker-secret dts114-clinic-app:v1.3.1
```

Open:

```text
http://127.0.0.1:5000/
http://127.0.0.1:5000/health
```

Local Docker proves the app runs inside a reproducible container. It is different from public deployment because it is still hosted on the local machine.

## Online Docker Deployment

Render deployment evidence:

| Check | URL |
|---|---|
| Public website | https://dts114-clinic-appointment-generator-g8md.onrender.com/ |
| Health check | https://dts114-clinic-appointment-generator-g8md.onrender.com/health |

Expected health response includes:

```json
{
  "service": "clinic-appointment-generator",
  "status": "ok",
  "storage": "sqlite",
  "version": "v1.3.1"
}
```

Online deployment is evidenced by:

- GitHub repository history.
- GitHub Actions CI/CD run.
- Render Docker build and public service.
- Public `/health` endpoint.
- Deployment screenshot in `Task2/screenshots/02_deployed_website.png`.

## Screenshot Evidence

| Required screenshot | File | What it should show |
|---|---|---|
| Commit records | `Task2/screenshots/01_commit_records.png` | GitHub commit history with meaningful development commits |
| Deployed website | `Task2/screenshots/02_deployed_website.png` | Render public website running the generated app |
| CI/CD workflow | `Task2/screenshots/03_cicd_workflow.png` | GitHub Actions workflow with passing checks |

After replacing or refreshing screenshots, run:

```bash
python scripts/validate_submission.py --require-screenshots
```

## Files That Must Not Be Submitted

Do not include:

- `.env`
- API keys or copied API-key screenshots
- `__pycache__/`
- `.pytest_cache/`
- Runtime SQLite database files such as `Task2/clinic_app/data/clinic.sqlite3`
- Runtime uploaded doctor photos unless they are deliberately submitted as evidence

The repository already ignores these runtime files through `.gitignore`.

## Suggested Cleanup Before Zipping

Run from the repository root:

```powershell
Remove-Item -Recurse -Force Task2/clinic_app/.pytest_cache -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force Task2/clinic_app/__pycache__ -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force Task2/clinic_app/tests/__pycache__ -ErrorAction SilentlyContinue
Remove-Item -Force Task2/clinic_app/data/clinic.sqlite3 -ErrorAction SilentlyContinue
```

Do not delete committed generated images, generated doctor photos, screenshots, or artefacts.

## Final Student Checks

- [ ] I can explain why this is a specialised generator for a clinic appointment problem.
- [ ] I can explain how a minor problem-statement change can still be handled by Task 1.
- [ ] I can explain how DeepSeek supports SDLC artefact generation.
- [ ] I can explain how APIFREE supports automatically generated website images.
- [ ] I can explain how Docker and Render demonstrate deployment differently.
- [ ] I can explain how Git commits, tests, CI/CD, and screenshots provide evidence.
- [ ] I can explain the safety boundary: appointment administration only, no diagnosis, no treatment advice, and no real patient records.
