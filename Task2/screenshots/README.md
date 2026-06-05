# Screenshot Evidence Guide

This folder stores real evidence screenshots for the DTS114 Software Component. These images support the version control, deployment, and CI/CD marking areas.

## Screenshot Set

| File | Evidence type | What it proves |
|---|---|---|
| `01_commit_records.png` | Git and version control | The project was developed through meaningful commits instead of one final upload |
| `02_deployed_website.png` | Online deployment | The generated Flask website is live on Render Docker and displays the generated image workflow |
| `03_cicd_workflow.png` | CI/CD | GitHub Actions validated the repository with tests, submission checks, Docker build, and smoke test |

## 1. Commit Records

Capture the GitHub commit history page after pushing the repository.

The screenshot should show evidence such as:

- Initial coursework scaffold and Task 1 notebook.
- Requirements, UML, and generated artefact work.
- Flask API and website generation.
- Testing, CI/CD, Docker, and Render deployment files.
- Role-based workflow, generated images, doctor schedule, and final polish.
- Version-aware commit messages or tags such as `v1.3.1`.

Suggested file:

```text
01_commit_records.png
```

## 2. Deployed Website

Capture the public Render website, not only the local Flask server.

Primary URL:

```text
https://dts114-clinic-appointment-generator-g8md.onrender.com/
```

The screenshot should show:

- The login page or role dashboard.
- The generated clinic image or generated doctor imagery.
- The public Render browser URL.
- A professional view of the generated appointment system.

Suggested file:

```text
02_deployed_website.png
```

## 3. CI/CD Workflow

Capture the successful GitHub Actions workflow run.

The screenshot should show:

- The repository Actions page or workflow run detail.
- A successful run status.
- Evidence that tests and validation ran.
- If visible, the Docker build or smoke test step.

Suggested file:

```text
03_cicd_workflow.png
```

## Validation Command

After adding or replacing screenshots, run from the repository root:

```bash
python scripts/validate_submission.py --require-screenshots
```

The validation script checks that all three screenshots exist and are non-empty.

## Evidence Boundary

Screenshots should not contain API keys, `.env` values, private tokens, or personal data. The software uses fictional demo data only.

If a screenshot is refreshed after a documentation-only commit, it is acceptable for the commit history screenshot to show the documentation commit as the latest item. The important point is that the earlier development history remains visible.
