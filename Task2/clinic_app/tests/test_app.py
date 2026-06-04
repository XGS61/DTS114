import json
import io
import sqlite3
from datetime import date, timedelta
from pathlib import Path

import pytest

from app import APPOINTMENT_TYPES, DEFAULT_DOCTOR_ID, DEMO_USERS, DOCTOR_ROSTER, create_app


PRIMARY_DOCTOR = DOCTOR_ROSTER[0]
SECONDARY_DOCTOR = DOCTOR_ROSTER[1]
TERTIARY_DOCTOR = DOCTOR_ROSTER[2]


def slot_for(doctor, offset=0):
    hour, minute = [int(part) for part in doctor["start_time"].split(":")]
    total_minutes = hour * 60 + minute + offset * int(doctor["slot_minutes"])
    return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"


def focus_type(doctor):
    return doctor["appointment_focus"] if doctor["appointment_focus"] in APPOINTMENT_TYPES else APPOINTMENT_TYPES[0]


def future_weekday(offset=2):
    candidate = date.today() + timedelta(days=offset)
    while candidate.weekday() >= 5:
        candidate += timedelta(days=1)
    return candidate.isoformat()


def future_weekend():
    candidate = date.today() + timedelta(days=2)
    while candidate.weekday() < 5:
        candidate += timedelta(days=1)
    return candidate.isoformat()


@pytest.fixture()
def client(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": tmp_path / "appointments.json",
            "UPLOAD_FOLDER": tmp_path / "uploads" / "doctors",
        }
    )
    return app.test_client()


def login(client, username="doctor", password="doctor123"):
    return client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    )


def register(client, **overrides):
    payload = {
        "display_name": "Jordan Smith",
        "username": "jordansmith",
        "role": "patient",
        "password": "SecurePass123",
        "confirm_password": "SecurePass123",
    }
    payload.update(overrides)
    return client.post("/api/auth/register", json=payload)


def admin_create_doctor(client, **overrides):
    payload = {
        "username": "doctorlee",
        "password": "DoctorPass123",
        "display_name": "Dr Lee Carter",
        "name": "Dr Lee Carter",
        "department": "Primary Care",
        "room": "Consulting Room 4A",
        "appointment_focus": APPOINTMENT_TYPES[0],
        "status": "On duty",
        "start_time": "09:00",
        "end_time": "12:00",
        "slot_minutes": 30,
        "capacity": 2,
        "profile": "Fictional demo clinician added by admin for appointment administration.",
    }
    payload.update(overrides)
    return client.post("/api/admin/doctors", json=payload)


def create_valid_appointment(client, **overrides):
    payload = {
        "patient_name": "Alex Chen",
        "contact_email": "alex@example.com",
        "preferred_date": future_weekday(),
        "preferred_time": slot_for(PRIMARY_DOCTOR, 1),
        "appointment_type": APPOINTMENT_TYPES[0],
        "reason": "Administrative booking request",
    }
    payload.update(overrides)
    return client.post("/api/appointments", json=payload)


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"
    assert response.get_json()["storage"] == "sqlite"


def test_demo_credentials_are_hashed_and_invalid_password_fails(client):
    assert DEMO_USERS["doctor"]["password_hash"] != "doctor123"
    assert "password_hash" in DEMO_USERS["doctor"]
    response = login(client, "doctor", "wrong-password")
    assert response.status_code == 401


def test_login_returns_role_redirect(client):
    response = login(client, "doctor", "doctor123")
    data = response.get_json()
    assert response.status_code == 200
    assert data["user"]["role"] == "doctor"
    assert data["redirect"] == "/app/staff"


def test_register_patient_account_redirects_to_patient_dashboard(client):
    response = register(client)
    data = response.get_json()
    session_response = client.get("/api/auth/session").get_json()

    assert response.status_code == 201
    assert data["user"]["username"] == "jordansmith"
    assert data["user"]["role"] == "patient"
    assert data["redirect"] == "/app/patient"
    assert session_response["authenticated"] is True
    assert session_response["user"]["is_demo"] is False


def test_register_staff_account_redirects_to_staff_dashboard(client):
    response = register(
        client,
        display_name="Dr Taylor Morgan",
        username="taylormorgan",
        role="doctor",
    )
    data = response.get_json()

    assert response.status_code == 201
    assert data["user"]["role"] == "doctor"
    assert data["user"]["doctor_id"]
    assert data["redirect"] == "/app/staff"
    profile_response = client.get("/api/doctors/me")
    assert profile_response.status_code == 200
    assert profile_response.get_json()["doctor"]["name"] == "Dr Taylor Morgan"


def test_register_rejects_duplicate_and_invalid_role(client):
    first = register(client, username="casey")
    duplicate = register(client, username="casey")
    invalid_role = register(client, username="newcasey", role="owner")

    assert first.status_code == 201
    assert duplicate.status_code == 409
    assert "already registered" in duplicate.get_json()["error"]
    assert invalid_role.status_code == 400
    assert "role must be" in invalid_role.get_json()["error"]


def test_registered_account_persists_and_can_login_between_app_instances(tmp_path):
    database_path = tmp_path / "clinic.sqlite3"
    first_app = create_app({"TESTING": True, "DATABASE": database_path})
    first_client = first_app.test_client()
    response = register(
        first_client,
        display_name="Riley Patient",
        username="rileypatient",
        role="patient",
        password="PatientPass123",
        confirm_password="PatientPass123",
    )
    assert response.status_code == 201

    second_app = create_app({"TESTING": True, "DATABASE": database_path})
    second_client = second_app.test_client()
    login_response = login(second_client, "rileypatient", "PatientPass123")
    assert login_response.status_code == 200
    assert login_response.get_json()["redirect"] == "/app/patient"


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


@pytest.mark.parametrize(
    "overrides, expected_error",
    [
        ({"preferred_date": date.today().isoformat()}, "future date"),
        ({"preferred_date": future_weekend()}, "weekday"),
        ({"preferred_time": "08:30"}, "clinic hours"),
        ({"preferred_time": "09:15"}, "30-minute"),
        ({"appointment_type": "Clinical diagnosis request"}, "configured appointment booking types"),
    ],
)
def test_appointment_business_rule_validation(client, overrides, expected_error):
    login(client, "patient", "patient123")
    response = create_valid_appointment(client, **overrides)
    assert response.status_code == 400
    assert expected_error in response.get_json()["error"]


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


def test_sqlite_database_initializes_and_persists_between_app_instances(tmp_path):
    database_path = tmp_path / "clinic.sqlite3"
    first_app = create_app({"TESTING": True, "DATABASE": database_path})
    first_client = first_app.test_client()
    login(first_client, "patient", "patient123")
    created = create_valid_appointment(first_client).get_json()["appointment"]

    second_app = create_app({"TESTING": True, "DATABASE": database_path})
    second_client = second_app.test_client()
    login(second_client, "doctor", "doctor123")
    payload = second_client.get("/api/appointments").get_json()

    assert database_path.exists()
    assert payload["count"] == 1
    assert payload["items"][0]["id"] == created["id"]


def test_sqlite_schema_contains_appointments_and_audit_tables(client, tmp_path):
    login(client, "patient", "patient123")
    create_valid_appointment(client)
    database_path = tmp_path / "unused.sqlite3"
    app = create_app({"TESTING": True, "DATABASE": database_path})
    assert app.config["DATABASE"] == database_path

    connection = sqlite3.connect(database_path)
    table_names = {
        row[0]
        for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    connection.close()
    assert {"appointments", "audit_events", "doctors", "doctor_shifts", "users"}.issubset(table_names)


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


def test_availability_endpoint_marks_occupied_slot(client):
    login(client, "patient", "patient123")
    appointment_date = future_weekday()
    booked_time = slot_for(PRIMARY_DOCTOR, 1)
    create_valid_appointment(client, preferred_date=appointment_date, preferred_time=booked_time)
    response = client.get(f"/api/availability?date={appointment_date}")
    data = response.get_json()
    slot = next(item for item in data["slots"] if item["time"] == booked_time)
    assert response.status_code == 200
    assert data["clinic_hours"]["slot_minutes"] == 30
    assert slot["available"] is False
    assert slot["occupied_count"] == 1


def test_today_doctors_endpoint_returns_roster_with_generated_photo_paths(client):
    login(client, "patient", "patient123")
    response = client.get("/api/doctors/today")
    data = response.get_json()
    assert response.status_code == 200
    assert data["service_date"]
    assert len(data["doctors"]) == len(DOCTOR_ROSTER)
    assert {doctor["department"] for doctor in data["doctors"]} == {
        doctor["department"] for doctor in DOCTOR_ROSTER
    }
    assert all(doctor["photo"].startswith("doctors/") for doctor in data["doctors"])


def test_doctors_endpoint_returns_selected_date_schedule_and_capacity(client):
    login(client, "patient", "patient123")
    appointment_date = future_weekday()
    response = client.get(f"/api/doctors?date={appointment_date}")
    data = response.get_json()
    assert response.status_code == 200
    assert data["service_date"] == appointment_date
    assert len(data["doctors"]) == 3
    expected_capacity = {doctor["id"]: doctor["capacity"] for doctor in DOCTOR_ROSTER}
    assert all(doctor["capacity"] == expected_capacity[doctor["id"]] for doctor in data["doctors"])
    assert all(doctor["available_slots"] >= 0 for doctor in data["doctors"])


def test_doctor_specific_availability_marks_only_selected_doctor_slot(client):
    appointment_date = future_weekday()
    primary_time = slot_for(PRIMARY_DOCTOR, 1)
    secondary_time = slot_for(SECONDARY_DOCTOR, 0)
    login(client, "patient", "patient123")
    create_valid_appointment(
        client,
        doctor_id=PRIMARY_DOCTOR["id"],
        preferred_date=appointment_date,
        preferred_time=primary_time,
    )
    primary = client.get(f"/api/doctors/{PRIMARY_DOCTOR['id']}/availability?date={appointment_date}").get_json()
    secondary = client.get(f"/api/doctors/{SECONDARY_DOCTOR['id']}/availability?date={appointment_date}").get_json()
    primary_slot = next(item for item in primary["slots"] if item["time"] == primary_time)
    secondary_slot = next(item for item in secondary["slots"] if item["time"] == secondary_time)
    assert primary_slot["available"] is False
    assert primary_slot["occupied_count"] == 1
    assert secondary_slot["available"] is True


def test_create_appointment_with_selected_doctor(client):
    appointment_date = future_weekday()
    login(client, "patient", "patient123")
    response = create_valid_appointment(
        client,
        doctor_id=SECONDARY_DOCTOR["id"],
        preferred_date=appointment_date,
        preferred_time=slot_for(SECONDARY_DOCTOR, 0),
        appointment_type=focus_type(SECONDARY_DOCTOR),
    )
    appointment = response.get_json()["appointment"]
    assert response.status_code == 201
    assert appointment["doctor_id"] == SECONDARY_DOCTOR["id"]
    assert appointment["doctor"]["name"] == SECONDARY_DOCTOR["name"]


def test_legacy_appointment_without_doctor_id_uses_default_doctor(client):
    login(client, "patient", "patient123")
    response = create_valid_appointment(client)
    appointment = response.get_json()["appointment"]
    assert response.status_code == 201
    assert appointment["doctor_id"] == DEFAULT_DOCTOR_ID


def test_capacity_conflict_is_per_doctor_slot(client):
    appointment_date = future_weekday()
    login(client, "patient", "patient123")
    first = create_valid_appointment(
        client,
        doctor_id=PRIMARY_DOCTOR["id"],
        preferred_date=appointment_date,
        preferred_time=slot_for(PRIMARY_DOCTOR, 1),
    ).get_json()["appointment"]
    second = create_valid_appointment(
        client,
        doctor_id=PRIMARY_DOCTOR["id"],
        patient_name="Sam Lee",
        preferred_date=appointment_date,
        preferred_time=slot_for(PRIMARY_DOCTOR, 1),
    ).get_json()["appointment"]
    third = create_valid_appointment(
        client,
        doctor_id=SECONDARY_DOCTOR["id"],
        patient_name="Taylor Green",
        preferred_date=appointment_date,
        preferred_time=slot_for(SECONDARY_DOCTOR, 0),
    ).get_json()["appointment"]
    items = client.get("/api/appointments").get_json()["items"]
    by_id = {item["id"]: item for item in items}
    assert by_id[first["id"]]["conflict"] is True
    assert by_id[second["id"]]["conflict"] is True
    assert by_id[third["id"]]["conflict"] is False


def test_patient_can_reschedule_own_pending_request_and_audit_records_it(client):
    original_date = future_weekday()
    new_date = future_weekday(5)
    login(client, "patient", "patient123")
    created = create_valid_appointment(
        client,
        doctor_id=PRIMARY_DOCTOR["id"],
        preferred_date=original_date,
        preferred_time=slot_for(PRIMARY_DOCTOR, 1),
    ).get_json()["appointment"]

    response = client.patch(
        f"/api/appointments/{created['id']}/reschedule",
        json={
            "doctor_id": SECONDARY_DOCTOR["id"],
            "preferred_date": new_date,
            "preferred_time": slot_for(SECONDARY_DOCTOR, 0),
        },
    )
    appointment = response.get_json()["appointment"]

    assert response.status_code == 200
    assert appointment["doctor_id"] == SECONDARY_DOCTOR["id"]
    assert appointment["preferred_date"] == new_date
    assert appointment["preferred_time"] == slot_for(SECONDARY_DOCTOR, 0)
    assert appointment["reschedule_history"][0]["from"]["doctor_id"] == PRIMARY_DOCTOR["id"]

    client.post("/api/auth/logout")
    login(client, "admin", "admin123")
    audit = client.get(f"/api/appointments/{created['id']}/audit").get_json()["events"]
    assert "rescheduled" in [event["action"] for event in audit]


def test_patient_cannot_reschedule_confirmed_request(client):
    new_date = future_weekday(5)
    login(client, "patient", "patient123")
    created = create_valid_appointment(client).get_json()["appointment"]

    client.post("/api/auth/logout")
    login(client, "doctor", "doctor123")
    client.patch(
        f"/api/appointments/{created['id']}/review",
        json={"status": "Confirmed", "review_note": "Slot is available."},
    )

    client.post("/api/auth/logout")
    login(client, "patient", "patient123")
    response = client.patch(
        f"/api/appointments/{created['id']}/reschedule",
        json={
            "doctor_id": SECONDARY_DOCTOR["id"],
            "preferred_date": new_date,
            "preferred_time": slot_for(SECONDARY_DOCTOR, 0),
        },
    )
    assert response.status_code == 400
    assert "Pending Review" in response.get_json()["error"]


def test_staff_reschedule_requires_review_note(client):
    new_date = future_weekday(5)
    login(client, "patient", "patient123")
    created = create_valid_appointment(client).get_json()["appointment"]

    client.post("/api/auth/logout")
    login(client, "admin", "admin123")
    response = client.patch(
        f"/api/appointments/{created['id']}/reschedule",
        json={
            "doctor_id": SECONDARY_DOCTOR["id"],
            "preferred_date": new_date,
            "preferred_time": slot_for(SECONDARY_DOCTOR, 0),
            "review_note": "",
        },
    )
    assert response.status_code == 400
    assert "review_note is required" in response.get_json()["error"]


def test_staff_can_reschedule_confirmed_request_with_note(client):
    new_date = future_weekday(5)
    login(client, "patient", "patient123")
    created = create_valid_appointment(client).get_json()["appointment"]

    client.post("/api/auth/logout")
    login(client, "admin", "admin123")
    client.patch(
        f"/api/appointments/{created['id']}/review",
        json={"status": "Confirmed", "review_note": "Slot is available."},
    )
    response = client.patch(
        f"/api/appointments/{created['id']}/reschedule",
        json={
            "doctor_id": TERTIARY_DOCTOR["id"],
            "preferred_date": new_date,
            "preferred_time": slot_for(TERTIARY_DOCTOR, 1),
            "review_note": "Confirmed appointment moved to a later doctor shift.",
        },
    )
    appointment = response.get_json()["appointment"]
    audit = client.get(f"/api/appointments/{created['id']}/audit").get_json()["events"]

    assert response.status_code == 200
    assert appointment["status"] == "Confirmed"
    assert appointment["doctor_id"] == TERTIARY_DOCTOR["id"]
    assert appointment["review_note"] == "Confirmed appointment moved to a later doctor shift."
    assert [event["action"] for event in audit][-1] == "rescheduled"


def test_schedule_day_endpoint_requires_staff_and_groups_by_doctor(client):
    appointment_date = future_weekday()
    login(client, "patient", "patient123")
    created = create_valid_appointment(
        client,
        doctor_id=SECONDARY_DOCTOR["id"],
        preferred_date=appointment_date,
        preferred_time=slot_for(SECONDARY_DOCTOR, 0),
    ).get_json()["appointment"]
    patient_response = client.get(f"/api/schedule/day?date={appointment_date}")
    assert patient_response.status_code == 403

    client.post("/api/auth/logout")
    login(client, "admin", "admin123")
    response = client.get(f"/api/schedule/day?date={appointment_date}")
    payload = response.get_json()
    secondary_schedule = next(
        entry for entry in payload["doctors"] if entry["doctor"]["id"] == SECONDARY_DOCTOR["id"]
    )
    booked_slot = next(slot for slot in secondary_schedule["slots"] if slot["time"] == slot_for(SECONDARY_DOCTOR, 0))

    assert response.status_code == 200
    assert payload["date"] == appointment_date
    assert booked_slot["appointments"][0]["id"] == created["id"]


def test_doctor_account_sees_only_linked_doctor_queue(client):
    appointment_date = future_weekday()
    login(client, "patient", "patient123")
    own = create_valid_appointment(
        client,
        doctor_id=PRIMARY_DOCTOR["id"],
        preferred_date=appointment_date,
        preferred_time=slot_for(PRIMARY_DOCTOR, 0),
    ).get_json()["appointment"]
    other = create_valid_appointment(
        client,
        doctor_id=SECONDARY_DOCTOR["id"],
        preferred_date=appointment_date,
        preferred_time=slot_for(SECONDARY_DOCTOR, 0),
        appointment_type=focus_type(SECONDARY_DOCTOR),
    ).get_json()["appointment"]

    client.post("/api/auth/logout")
    login(client, "doctor", "doctor123")
    queue = client.get("/api/appointments").get_json()
    hidden_detail = client.get(f"/api/appointments/{other['id']}")
    hidden_review = client.patch(
        f"/api/appointments/{other['id']}/review",
        json={"status": "Confirmed", "review_note": "Reviewed by linked doctor."},
    )
    schedule = client.get(f"/api/schedule/day?date={appointment_date}").get_json()

    assert queue["count"] == 1
    assert queue["items"][0]["id"] == own["id"]
    assert hidden_detail.status_code == 403
    assert hidden_review.status_code == 403
    assert [entry["doctor"]["id"] for entry in schedule["doctors"]] == [PRIMARY_DOCTOR["id"]]

    client.post("/api/auth/logout")
    login(client, "admin", "admin123")
    admin_queue = client.get("/api/appointments").get_json()
    assert admin_queue["count"] == 2


def test_doctor_can_update_own_profile_and_patient_roster_reflects_it(client):
    appointment_date = future_weekday()
    login(client, "doctor", "doctor123")
    response = client.patch(
        "/api/doctors/me",
        json={
            "name": "Dr Amelia Hart",
            "department": "Updated Care Coordination",
            "room": "Consulting Room 8C",
            "appointment_focus": APPOINTMENT_TYPES[0],
            "status": "Limited availability",
            "start_time": "10:00",
            "end_time": "13:00",
            "slot_minutes": 30,
            "capacity": 2,
            "profile": "Updated fictional clinician profile for appointment administration.",
        },
    )
    assert response.status_code == 200
    doctor = response.get_json()["doctor"]
    assert doctor["department"] == "Updated Care Coordination"
    assert doctor["capacity"] == 2

    client.post("/api/auth/logout")
    login(client, "patient", "patient123")
    doctors = client.get(f"/api/doctors?date={appointment_date}").get_json()["doctors"]
    updated = next(item for item in doctors if item["id"] == PRIMARY_DOCTOR["id"])
    assert updated["department"] == "Updated Care Coordination"
    assert updated["room"] == "Consulting Room 8C"
    assert updated["capacity"] == 2


def test_admin_can_create_doctor_account_visible_to_patient_and_doctor_login(client):
    appointment_date = future_weekday()
    login(client, "admin", "admin123")
    create_response = admin_create_doctor(client)
    payload = create_response.get_json()
    assert create_response.status_code == 201
    assert payload["user"]["role"] == "doctor"
    assert payload["user"]["doctor_id"] == payload["doctor"]["id"]

    admin_list = client.get("/api/admin/doctors").get_json()["doctors"]
    assert payload["doctor"]["id"] in {doctor["id"] for doctor in admin_list}

    client.post("/api/auth/logout")
    login(client, "patient", "patient123")
    doctors = client.get(f"/api/doctors?date={appointment_date}").get_json()["doctors"]
    created_doctor = next(doctor for doctor in doctors if doctor["id"] == payload["doctor"]["id"])
    assert created_doctor["department"] == "Primary Care"
    assert created_doctor["photo"].startswith("/api/doctors/")

    client.post("/api/auth/logout")
    login_response = login(client, "doctorlee", "DoctorPass123")
    assert login_response.status_code == 200
    profile = client.get("/api/doctors/me").get_json()["doctor"]
    assert profile["id"] == payload["doctor"]["id"]


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


def test_review_endpoint_requires_review_note(client):
    login(client, "patient", "patient123")
    created = create_valid_appointment(client).get_json()["appointment"]
    client.post("/api/auth/logout")
    login(client, "doctor", "doctor123")
    response = client.patch(
        f"/api/appointments/{created['id']}/review",
        json={"status": "Confirmed", "review_note": ""},
    )
    assert response.status_code == 400
    assert "review_note is required" in response.get_json()["error"]


def test_patient_can_cancel_own_request_and_audit_records_it(client):
    login(client, "patient", "patient123")
    created = create_valid_appointment(client).get_json()["appointment"]
    response = client.patch(
        f"/api/appointments/{created['id']}/cancel",
        json={"reason": "Patient no longer needs this appointment."},
    )
    assert response.status_code == 200
    assert response.get_json()["appointment"]["status"] == "Cancelled"

    client.post("/api/auth/logout")
    login(client, "doctor", "doctor123")
    audit = client.get(f"/api/appointments/{created['id']}/audit").get_json()["events"]
    assert [event["action"] for event in audit] == ["created", "patient_cancelled"]


def test_patient_cannot_view_audit_endpoint(client):
    login(client, "patient", "patient123")
    created = create_valid_appointment(client).get_json()["appointment"]
    response = client.get(f"/api/appointments/{created['id']}/audit")
    assert response.status_code == 403


def test_audit_records_create_review_and_conflict_updates(client):
    login(client, "patient", "patient123")
    first = create_valid_appointment(client).get_json()["appointment"]
    second = create_valid_appointment(client, patient_name="Sam Lee").get_json()["appointment"]
    client.post("/api/auth/logout")
    login(client, "doctor", "doctor123")
    client.patch(
        f"/api/appointments/{second['id']}/review",
        json={"status": "Cancelled", "review_note": "Resolve duplicate slot."},
    )
    first_audit = client.get(f"/api/appointments/{first['id']}/audit").get_json()["events"]
    second_audit = client.get(f"/api/appointments/{second['id']}/audit").get_json()["events"]
    assert "created" in [event["action"] for event in first_audit]
    assert "conflict_updated" in [event["action"] for event in first_audit]
    assert "reviewed" in [event["action"] for event in second_audit]


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


def test_list_endpoint_supports_status_date_search_and_pagination(client):
    appointment_date = future_weekday()
    login(client, "patient", "patient123")
    create_valid_appointment(
        client,
        patient_name="Alex Searchable",
        preferred_date=appointment_date,
        preferred_time=slot_for(PRIMARY_DOCTOR, 0),
        reason="Insurance document appointment",
    )
    create_valid_appointment(
        client,
        patient_name="Bailey Other",
        preferred_date=appointment_date,
        preferred_time=slot_for(PRIMARY_DOCTOR, 1),
        reason="Administrative booking request",
    )
    client.post("/api/auth/logout")
    login(client, "doctor", "doctor123")
    response = client.get(
        f"/api/appointments?status=Pending%20Review&date={appointment_date}&q=insurance&page=1&page_size=1"
    )
    payload = response.get_json()
    assert response.status_code == 200
    assert payload["count"] == 1
    assert payload["page"] == 1
    assert payload["page_size"] == 1
    assert payload["items"][0]["patient_name"] == "Alex Searchable"


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
    assert 'data-calendar-today>Next Weekday</button>' in page
    assert 'name="preferred_time" type="time"' in page


def test_patient_page_includes_today_doctor_roster_panel(client):
    login(client, "patient", "patient123")
    response = client.get("/app/patient")
    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Today's Doctors" in page
    assert 'id="doctorRosterList"' in page
    assert "/api/doctors/today" in Path(__file__).resolve().parents[1].joinpath("static", "app.js").read_text(encoding="utf-8")


def test_staff_page_includes_operational_dashboard_controls(client):
    login(client, "doctor", "doctor123")
    response = client.get("/app/staff")
    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Your Appointment Queue" in page
    assert 'id="doctorProfileForm"' in page
    assert 'id="doctorPhotoForm"' in page
    assert 'id="staffSearch"' in page
    assert 'id="detailDrawer"' in page
    assert 'id="reviewModal"' in page
    assert "Audit Timeline" in page


def test_doctor_can_upload_own_photo_and_patient_roster_uses_it(client):
    login(client, "doctor", "doctor123")
    image_bytes = b"\x89PNG\r\n\x1a\n" + b"prototype image bytes"
    response = client.post(
        "/api/doctors/me/photo",
        data={"photo": (io.BytesIO(image_bytes), "profile.png")},
        content_type="multipart/form-data",
    )
    data = response.get_json()
    stored_path = data["doctor"]["photo"]

    assert response.status_code == 200
    assert stored_path.startswith("uploads/doctors/")
    assert Path(client.application.config["UPLOAD_FOLDER"]).joinpath(Path(stored_path).name).exists()

    client.post("/api/auth/logout")
    login(client, "patient", "patient123")
    roster = client.get(f"/api/doctors?date={future_weekday()}").get_json()["doctors"]
    primary = next(doctor for doctor in roster if doctor["id"] == DEFAULT_DOCTOR_ID)
    assert primary["photo"] == stored_path


def test_patient_cannot_upload_doctor_photo(client):
    login(client, "patient", "patient123")
    response = client.post(
        "/api/doctors/me/photo",
        data={"photo": (io.BytesIO(b"\x89PNG\r\n\x1a\npatient bytes"), "patient.png")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 403


def test_admin_page_includes_doctor_account_management(client):
    login(client, "admin", "admin123")
    response = client.get("/app/staff")
    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "All Appointment Queues" in page
    assert 'id="adminDoctorForm"' in page
    assert 'id="adminDoctorList"' in page


def test_legacy_patient_route_still_works(client):
    login(client, "patient", "patient123")
    response = client.get("/patient")
    assert response.status_code == 200


def test_root_renders_login_page_for_public_deployment(client):
    response = client.get("/")
    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Sign In" in page
    assert "Sign up" in page
    assert 'href="/app/register"' in page
    assert 'id="registerForm"' not in page
    assert "Clinic Appointment System" in page


def test_register_page_renders_sign_up_form(client):
    response = client.get("/register")
    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Sign Up" in page
    assert 'id="registerForm"' in page
    assert "Account role" in page
    assert "Already have an account?" in page


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
    assert metadata["model"] == "Qwen/Qwen-Image"
    assert metadata["status"] in {"generated", "fallback"}
    assert "appointment system" in metadata["prompt"].lower()
    assert "no medical diagnosis content" in metadata["prompt"].lower()
    assert image_path.exists()
    signature = image_path.read_bytes()[:12]
    assert signature.startswith(b"\x89PNG") or signature.startswith(b"\xff\xd8\xff") or signature.startswith(b"RIFF")


def test_apifree_doctor_photo_metadata_records_roster_images():
    app_dir = Path(__file__).resolve().parents[1]
    metadata_path = app_dir / "artifacts" / "doctor_photo_generation_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["generator"] == "APIFREE API"
    assert metadata["asset_type"] == "doctor_roster_photos"
    assert len(metadata["assets"]) == len(DOCTOR_ROSTER)
    for asset in metadata["assets"]:
        image_path = app_dir / asset["output"]
        assert asset["doctor_id"] in {doctor["id"] for doctor in DOCTOR_ROSTER}
        assert asset["status"] in {"generated", "fallback"}
        assert image_path.exists()
        signature = image_path.read_bytes()[:12]
        assert signature.startswith(b"\x89PNG") or signature.startswith(b"\xff\xd8\xff") or signature.startswith(b"RIFF")


def test_release_metadata_records_version_and_evidence_paths():
    metadata_path = Path(__file__).resolve().parents[1] / "artifacts" / "release_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["app_version"] == "v1.3.0"
    assert metadata["methodology"] == "AI-DLC-informed iterative methodology"
    assert "Task1/clinic_appointment_generator.ipynb" in metadata["evidence_paths"]["generator_notebook"]
