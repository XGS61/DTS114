# AI Use Statement

This software component uses AI as an engineering support tool, not as a substitute for student reflection or final report writing.

## Where AI Is Used

- The Task 1 notebook can call the DeepSeek Chat Completions API when `ENABLE_LLM_GENERATION=1` and `DEEPSEEK_API_KEY` is configured.
- DeepSeek is used to generate draft SDLC artefacts: requirements, user stories, validation checklist, and UML source.
- The generated run is recorded in `Task2/clinic_app/artifacts/deepseek_generation_metadata.json`, including model, endpoint, status, timestamp, and token usage.
- A generated clinic interface image is included in `Task2/clinic_app/static/generated_clinic_image.png` and displayed on the login page.

## Human Review and Validation

- The notebook applies deterministic post-processing to align AI output with the implemented Flask routes, evidence paths, and safety wording.
- Automated tests verify role access, conflict handling, non-diagnostic summaries, English-only date picker behaviour, and DeepSeek metadata.
- The validation script checks required files, single-notebook structure, DeepSeek metadata, Chinese text, and possible leaked API keys.

## Safety Boundary

- The prototype is for appointment administration only.
- It does not provide diagnosis, treatment advice, prescriptions, or real patient records.
- API keys are read from environment variables only and are not committed to the repository.

## Academic Integrity Boundary

The final handwritten report and presentation explanation should remain the student's own work. This project documentation is evidence of the software component and development process; it should support, not replace, the student's own analysis.
