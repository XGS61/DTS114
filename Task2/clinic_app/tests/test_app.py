import json
from pathlib import Path

import pytest

from app import create_app


@pytest.fixture()
def client(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": tmp_path / "appointments.json",
        }
    )
    return app.test_client()


def login(client, username="doctor", password="doctor123"):
    return client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    )


def create_valid_appointment(client, **overrides):
    payload = {
        "patient_name": "Alex Chen",
        "contact_email": "alex@example.com",
        "preferred_date": "2026-06-05",
        "preferred_time": "09:30",
        "appointment_type": "General consultation booking",
        "reason": "Administrative booking request",
    }
    payload.update(overrides)
    return client.post("/api/appointments", json=payload)


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_login_returns_role_redirect(client):
    response = login(client, "doctor", "doctor123")
    data = response.get_json()
    assert response.status_code == 200
    assert data["user"]["role"] == "doctor"
    assert data["redirect"] == "/app/staff"


def test_appointment_api_requires_login(client):
    create_response = create_valid_appointment(client)
    list_response = client.get("/api/appointments")
    summary_response = client.get("/api/appointments/1/summary")
    assert create_response.status_code == 401
    assert list_response.status_code == 401
    assert summary_response.status_code == 401


def test_create_appointment_validates_required_fields(client):
    login(client, "patient", "patient123")
    response = client.post("/api/appointments", json={"patient_name": "Alex"})
    assert response.status_code == 400
    assert "Missing required field" in response.get_json()["error"]


def test_patient_request_is_visible_to_staff_queue(client):
    login(client, "patient", "patient123")
    created = create_valid_appointment(client).get_json()["appointment"]
    patient_view = client.get("/api/appointments").get_json()
    assert patient_view["count"] == 1
    assert patient_view["items"][0]["id"] == created["id"]

    client.post("/api/auth/logout")
    login(client, "doctor", "doctor123")
    staff_view = client.get("/api/appointments").get_json()
    assert staff_view["count"] == 1
    assert staff_view["items"][0]["created_by"] == "patient"


def test_conflict_detection(client):
    login(client, "patient", "patient123")
    first = create_valid_appointment(client)
    second = create_valid_appointment(client, patient_name="Sam Lee")
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.get_json()["appointment"]["conflict"] is False
    assert second.get_json()["appointment"]["conflict"] is True
    visible_items = client.get("/api/appointments").get_json()["items"]
    assert all(item["conflict"] is True for item in visible_items)


def test_conflict_recalculation_after_cancellation(client):
    login(client, "patient", "patient123")
    first = create_valid_appointment(client).get_json()["appointment"]
    second = create_valid_appointment(client, patient_name="Sam Lee").get_json()["appointment"]

    client.post("/api/auth/logout")
    login(client, "doctor", "doctor123")
    response = client.patch(
        f"/api/appointments/{second['id']}/review",
        json={"status": "Cancelled", "review_note": "Slot conflict resolved."},
    )
    assert response.status_code == 200
    items = client.get("/api/appointments").get_json()["items"]
    first_after = next(item for item in items if item["id"] == first["id"])
    second_after = next(item for item in items if item["id"] == second["id"])
    assert first_after["conflict"] is False
    assert second_after["conflict"] is False


def test_review_endpoint_requires_staff_role(client):
    login(client, "patient", "patient123")
    created = create_valid_appointment(client).get_json()["appointment"]
    response = client.patch(
        f"/api/appointments/{created['id']}/review",
        json={"status": "Confirmed", "review_note": "Slot is available."},
    )
    assert response.status_code == 403
    assert "staff permission" in response.get_json()["error"]


def test_review_endpoint_updates_status_for_staff(client):
    login(client, "patient", "patient123")
    created = create_valid_appointment(client).get_json()["appointment"]
    client.post("/api/auth/logout")
    login(client, "doctor", "doctor123")
    response = client.patch(
        f"/api/appointments/{created['id']}/review",
        json={"status": "Confirmed", "review_note": "Slot is available."},
    )
    data = response.get_json()
    assert response.status_code == 200
    assert data["appointment"]["status"] == "Confirmed"
    assert data["appointment"]["review_note"] == "Slot is available."
    assert data["appointment"]["reviewed_role"] == "doctor"


def test_summary_is_non_diagnostic(client):
    login(client, "patient", "patient123")
    created = create_valid_appointment(client).get_json()["appointment"]
    response = client.get(f"/api/appointments/{created['id']}/summary")
    summary = response.get_json()["summary"].lower()
    assert response.status_code == 200
    assert "non-diagnostic" in summary
    assert "does not provide treatment advice" in summary


def test_rejects_diagnosis_or_treatment_requests(client):
    login(client, "patient", "patient123")
    response = create_valid_appointment(client, reason="Please diagnose my illness")
    assert response.status_code == 400
    assert "appointment administration" in response.get_json()["error"]


def test_patient_cannot_view_staff_created_appointment(client):
    login(client, "doctor", "doctor123")
    created = create_valid_appointment(client).get_json()["appointment"]

    client.post("/api/auth/logout")
    login(client, "patient", "patient123")
    list_response = client.get("/api/appointments")
    get_response = client.get(f"/api/appointments/{created['id']}")
    summary_response = client.get(f"/api/appointments/{created['id']}/summary")

    assert list_response.get_json()["count"] == 0
    assert get_response.status_code == 403
    assert summary_response.status_code == 403


def test_meta_requirements_describe_relevant_ai_tooling(client):
    response = client.get("/api/meta/requirements")
    data = response.get_json()
    assert response.status_code == 200
    tooling = data["requirements"]["ai_specific_tooling"]
    assert any("DeepSeek" in item for item in tooling)
    assert any("APIFREE" in item for item in tooling)
    assert any("Deterministic fallback" in item for item in tooling)


def test_patient_page_uses_english_custom_calendar_picker(client):
    login(client, "patient", "patient123")
    response = client.get("/app/patient")
    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert 'data-date-picker' in page
    assert 'placeholder="YYYY-MM-DD"' in page
    assert 'data-calendar-title' in page
    assert '<span>Sun</span><span>Mon</span><span>Tue</span>' in page
    assert 'data-calendar-clear>Clear</button>' in page
    assert 'data-calendar-today>Today</button>' in page
    assert 'name="preferred_time" type="time"' in page


def test_legacy_patient_route_still_works(client):
    login(client, "patient", "patient123")
    response = client.get("/patient")
    assert response.status_code == 200


def test_root_renders_login_page_for_public_deployment(client):
    response = client.get("/")
    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Demo Login" in page
    assert "Clinic Appointment System" in page

def test_deepseek_metadata_records_generated_artefact_run():
    metadata_path = Path(__file__).resolve().parents[1] / "artifacts" / "deepseek_generation_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["generator"] == "DeepSeek API"
    assert metadata["endpoint"] == "https://api.deepseek.com/chat/completions"
    assert metadata["model"] == "deepseek-v4-flash"
    assert metadata["status"] == "generated"
    assert metadata["usage"]["total_tokens"] > 0
    assert metadata["validation"]["summary_endpoint"] == "GET /api/appointments/<id>/summary"
    assert metadata["validation"]["auth_boundary"] == "Appointment APIs require an authenticated demo session"


def test_apifree_metadata_records_generated_image_run():
    app_dir = Path(__file__).resolve().parents[1]
    metadata_path = app_dir / "artifacts" / "apifree_image_generation_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    image_path = app_dir / metadata["output"]
    assert metadata["generator"] == "APIFREE API"
    assert metadata["provider"] == "APIFREE"
    assert metadata["model"] == "qwen/qwen-image-2512"
    assert metadata["status"] in {"generated", "fallback"}
    assert "clinic appointment system" in metadata["prompt"].lower()
    assert image_path.exists()
    assert image_path.read_bytes().startswith(b"\x89PNG")
