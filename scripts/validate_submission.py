import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    ".py",
    ".html",
    ".css",
    ".js",
    ".md",
    ".json",
    ".txt",
    ".yml",
    ".yaml",
    ".puml",
    ".ipynb",
    ".example",
}
SECRET_PATTERN = re.compile(r"(sk|rnd)_[A-Za-z0-9_-]{20,}")


REQUIRED_PATHS = [
    "Task1/clinic_appointment_generator.ipynb",
    "environment.yml",
    "Task2/clinic_app/app.py",
    "Task2/clinic_app/templates/login.html",
    "Task2/clinic_app/templates/patient.html",
    "Task2/clinic_app/templates/staff.html",
    "Task2/clinic_app/static/generated_clinic_image.png",
    "Task2/clinic_app/artifacts/deepseek_generation_metadata.json",
    "Task2/clinic_app/artifacts/apifree_image_generation_metadata.json",
    "Task2/clinic_app/artifacts/generated_requirements.md",
    "Task2/clinic_app/artifacts/generated_user_stories.json",
    "Task2/clinic_app/artifacts/generated_validation_checklist.md",
    "Task2/clinic_app/artifacts/diagrams/generated_use_case_diagram.puml",
    "Task2/clinic_app/artifacts/diagrams/sequence_diagram.puml",
    "Task2/clinic_app/artifacts/diagrams/activity_diagram.puml",
    "Task2/clinic_app/tests/test_app.py",
    "Task2/clinic_app/requirements.txt",
    "Task2/clinic_app/runtime.txt",
    "Task2/clinic_app/Dockerfile",
    "Task2/clinic_app/.dockerignore",
    "Task2/clinic_app/render.yaml",
    ".github/workflows/ci.yml",
    "render.yaml",
]

REQUIRED_SCREENSHOTS = [
    "Task2/screenshots/01_commit_records.png",
    "Task2/screenshots/02_deployed_website.png",
    "Task2/screenshots/03_cicd_workflow.png",
]


def iter_text_files():
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in {".gitignore"}:
            yield path


def assert_required_paths(require_screenshots):
    missing = [rel for rel in REQUIRED_PATHS if not (ROOT / rel).exists()]
    if require_screenshots:
        missing.extend(rel for rel in REQUIRED_SCREENSHOTS if not (ROOT / rel).exists())
    if missing:
        raise AssertionError("Missing required submission path(s): " + ", ".join(missing))


def assert_single_task1_notebook():
    notebooks = list((ROOT / "Task1").glob("*.ipynb"))
    if len(notebooks) != 1:
        raise AssertionError(f"Task1 must contain exactly one notebook, found {len(notebooks)}")


def assert_deepseek_metadata():
    metadata_path = ROOT / "Task2/clinic_app/artifacts/deepseek_generation_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("generator") != "DeepSeek API":
        raise AssertionError("DeepSeek metadata must record the DeepSeek API generator")
    if metadata.get("status") != "generated":
        raise AssertionError("DeepSeek metadata status must be generated")
    if metadata.get("usage", {}).get("total_tokens", 0) <= 0:
        raise AssertionError("DeepSeek metadata must record token usage")


def assert_apifree_image_metadata():
    metadata_path = ROOT / "Task2/clinic_app/artifacts/apifree_image_generation_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("generator") != "APIFREE API":
        raise AssertionError("APIFREE metadata must record the APIFREE API generator")
    if metadata.get("model") != "qwen/qwen-image-2512":
        raise AssertionError("APIFREE metadata must record the generated image model")
    if metadata.get("status") not in {"generated", "fallback"}:
        raise AssertionError("APIFREE metadata status must be generated or fallback")
    output_path = ROOT / "Task2/clinic_app" / metadata.get("output", "")
    if not output_path.exists():
        raise AssertionError("APIFREE metadata output image path does not exist")


def assert_no_chinese_or_secrets():
    chinese_hits = []
    secret_hits = []
    for path in iter_text_files():
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if any("\u4e00" <= char <= "\u9fff" for char in line):
                chinese_hits.append(f"{path.relative_to(ROOT)}:{line_number}")
            if SECRET_PATTERN.search(line):
                secret_hits.append(f"{path.relative_to(ROOT)}:{line_number}")
    if chinese_hits:
        raise AssertionError("Chinese text found in submission files: " + ", ".join(chinese_hits[:10]))
    if secret_hits:
        raise AssertionError("Possible API key found in submission files: " + ", ".join(secret_hits[:10]))


def main():
    parser = argparse.ArgumentParser(description="Validate DTS114 software submission structure.")
    parser.add_argument(
        "--require-screenshots",
        action="store_true",
        help="Require the three final evidence screenshots before packaging.",
    )
    args = parser.parse_args()

    assert_required_paths(args.require_screenshots)
    assert_single_task1_notebook()
    assert_deepseek_metadata()
    assert_apifree_image_metadata()
    assert_no_chinese_or_secrets()
    print("Submission validation passed.")


if __name__ == "__main__":
    main()
