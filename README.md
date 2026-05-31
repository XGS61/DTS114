# DTS114 Clinic Appointment Generator

This coursework software component implements an AI-DLC-informed generator for a Flask-based clinic appointment administration prototype.

The project demonstrates:

- SDLC artefact generation: requirements, user stories, acceptance criteria, UML source, and validation checklist.
- A generated Flask API and website for clinic appointment administration.
- A generated website image shown in the front end.
- Human review boundary: appointments are created as `Pending Review` and require receptionist confirmation or cancellation.
- Safety boundary: no diagnosis, no treatment advice, and no real patient records.
- Testing, CI/CD workflow, and deployment-ready Render configuration.

## Structure

```text
StudentID-Your_Name/
  Task1/
    clinic_appointment_generator.ipynb
  Task2/
    clinic_app/
      app.py
      requirements.txt
      render.yaml
      templates/
      static/
      tests/
      artifacts/
    screenshots/
  .github/workflows/
```

## Run Locally

```bash
cd Task2/clinic_app
python -m pip install -r requirements.txt
python app.py
```

Open:

- Website: http://127.0.0.1:5000
- Health check: http://127.0.0.1:5000/health

## Test

```bash
cd Task2/clinic_app
python -m pytest
```

## GitHub / Deployment Evidence

The `Task2/screenshots` folder explains the three required screenshots:

1. Git commit records.
2. Deployed website.
3. CI/CD workflow.

After creating an empty GitHub repository, add it as a remote and push:

```bash
git remote add origin <your-github-repository-url>
git branch -M main
git push -u origin main
```

## AI Use and Academic Integrity

This software includes generated artefact templates and deterministic generation logic to support learning. Final report and presentation wording should be written in the student's own words, with AI use acknowledged according to the module policy.
