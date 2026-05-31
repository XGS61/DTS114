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
    assert data["redirect"] == "/staff"


def test_create_appointment_validates_required_fields(client):
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
    first = create_valid_appointment(client)
    second = create_valid_appointment(client, patient_name="Sam Lee")
    assert first.status_code == 201
    assert second.status_code == 201
    assert second.get_json()["appointment"]["conflict"] is True


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
    created = create_valid_appointment(client).get_json()["appointment"]
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
    created = create_valid_appointment(client).get_json()["appointment"]
    response = client.get(f"/api/appointments/{created['id']}/summary")
    summary = response.get_json()["summary"].lower()
    assert response.status_code == 200
    assert "non-diagnostic" in summary
    assert "does not provide treatment advice" in summary


def test_rejects_diagnosis_or_treatment_requests(client):
    response = create_valid_appointment(client, reason="Please diagnose my illness")
    assert response.status_code == 400
    assert "appointment administration" in response.get_json()["error"]


def test_meta_requirements_describe_relevant_ai_tooling(client):
    response = client.get("/api/meta/requirements")
    data = response.get_json()
    assert response.status_code == 200
    tooling = data["requirements"]["ai_specific_tooling"]
    assert any("DeepSeek" in item for item in tooling)
    assert any("Deterministic fallback" in item for item in tooling)
