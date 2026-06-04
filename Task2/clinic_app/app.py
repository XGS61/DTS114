import json
import os
import sqlite3
from datetime import UTC, date, datetime, timedelta, time
from functools import wraps
from math import ceil
from pathlib import Path

from flask import Flask, Response, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


BASE_DIR = Path(__file__).resolve().parent
STAFF_ROLES = {"doctor", "admin", "receptionist"}
REGISTERABLE_ROLES = {"patient", "doctor", "admin"}
STATUS_VALUES = {"Pending Review", "Confirmed", "Cancelled"}
APPOINTMENT_TYPES = ['General consultation booking',
 'Vaccination appointment booking',
 'Follow-up appointment booking',
 'Administrative query booking']
CLINIC_OPEN_TIME = time(9, 0)
CLINIC_CLOSE_TIME = time(17, 0)
SLOT_MINUTES = 30
APP_VERSION = "v1.3.0"
MAX_DOCTOR_PHOTO_BYTES = 2 * 1024 * 1024
ALLOWED_DOCTOR_PHOTO_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
DOCTOR_ROSTER = [{'id': 'amelia-hart',
  'name': 'Dr Amelia Hart',
  'department': 'General Medicine',
  'start_time': '09:00',
  'end_time': '12:30',
  'shift': '09:00-12:30',
  'slot_minutes': 30,
  'capacity': 1,
  'room': 'Consulting Room 2A',
  'appointment_focus': 'General consultation booking',
  'status': 'On duty',
  'photo': 'doctors/dr_amelia_hart.png',
  'profile': 'Fictional demo clinician for administrative appointment routing.'},
 {'id': 'noah-bennett',
  'name': 'Dr Noah Bennett',
  'department': 'Preventive Care',
  'start_time': '10:00',
  'end_time': '15:00',
  'shift': '10:00-15:00',
  'slot_minutes': 30,
  'capacity': 1,
  'room': 'Consulting Room 3B',
  'appointment_focus': 'Vaccination appointment booking',
  'status': 'On duty',
  'photo': 'doctors/dr_noah_bennett.png',
  'profile': 'Fictional demo clinician for non-diagnostic appointment scheduling.'},
 {'id': 'priya-raman',
  'name': 'Dr Priya Raman',
  'department': 'Follow-up Coordination',
  'start_time': '13:00',
  'end_time': '17:00',
  'shift': '13:00-17:00',
  'slot_minutes': 30,
  'capacity': 1,
  'room': 'Consulting Room 1C',
  'appointment_focus': 'Follow-up appointment booking',
  'status': 'On duty',
  'photo': 'doctors/dr_priya_raman.png',
  'profile': 'Fictional demo clinician for reviewed appointment administration.'}]
DEFAULT_DOCTOR_ID = DOCTOR_ROSTER[0]["id"]


def _demo_user(password, role, display_name, doctor_id=None):
    return {
        "password_hash": generate_password_hash(password),
        "demo_password": password,
        "role": role,
        "display_name": display_name,
        "doctor_id": doctor_id,
    }


DEMO_USERS = {
    "patient": _demo_user("patient123", "patient", "Demo Patient"),
    "doctor": _demo_user("doctor123", "doctor", "Dr Amelia Hart", DEFAULT_DOCTOR_ID),
    "admin": _demo_user("admin123", "admin", "Clinic Admin"),
}


def create_app(test_config=None):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_mapping(
        SECRET_KEY=os.getenv("FLASK_SECRET_KEY", "dts114-demo-secret"),
        DATABASE=BASE_DIR / "data" / "clinic.sqlite3",
        UPLOAD_FOLDER=BASE_DIR / "static" / "uploads" / "doctors",
    )
    if test_config and "DATA_FILE" in test_config and "DATABASE" not in test_config:
        app.config["DATABASE"] = Path(test_config["DATA_FILE"]).with_suffix(".sqlite3")
    app.config.update(test_config or {})

    safety_boundary = {
        "scope": "Appointment administration prototype only",
        "not_allowed": [
            "diagnosis",
            "treatment advice",
            "prescriptions",
            "real patient records",
        ],
        "human_review": "Doctor or admin staff must confirm or cancel each appointment request.",
    }

    requirements_summary = {
        "methodology": "AI-DLC-informed iterative methodology",
        "inception": [
            "Define a clinic appointment administration problem",
            "Identify actors: Patient, Doctor, Admin Staff, Clinic System",
            "Set safety boundary: no diagnosis, no treatment advice, no real patient records",
        ],
        "construction": [
            "Generate requirements, user stories, UML source, Flask API, role-based website, APIFREE-backed images, tests, and validation evidence",
            "Validate generated artefacts against safety, role, workflow, scheduling, audit, and testing checklists",
        ],
        "operations": [
            "Use Git commits and version tags for traceability",
            "Run tests through CI/CD",
            "Deploy the Flask website/API with Docker and environment-variable based configuration",
        ],
        "ai_specific_tooling": [
            "Prompt templates and structured JSON artefacts in the notebook",
            "DeepSeek API support for SDLC artefact generation with recorded metadata",
            "APIFREE API support for generated clinic interface imagery and doctor roster photos with recorded metadata",
            "Deterministic fallback when API keys are not configured",
            "Submission validation script for structure, metadata, language, and secret checks",
        ],
        "industrial_upgrade": [
            "SQLite persistence with automatic schema creation",
            "Hashed demo credentials, self-registration, doctor-account linking, and role-based session routing",
            "Doctor schedule seed data, doctor-specific availability, pagination, search, patient cancellation, staff rescheduling, and audit trail",
            "Doctor accounts can see and decide only their own linked appointment queue",
            "Doctor accounts can maintain their own visible department, room, shift, capacity, and appointment focus",
            "Admin accounts can see every queue and create doctor accounts with matching patient-visible doctor profiles",
            "Production-style patient and staff workspaces while preserving the coursework safety boundary",
        ],
    }

    def _now():
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")

    def _database_path():
        return Path(app.config["DATABASE"])

    def _connect():
        path = _database_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db():
        with _connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS doctors (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    department TEXT NOT NULL,
                    room TEXT NOT NULL,
                    photo TEXT NOT NULL,
                    appointment_focus TEXT NOT NULL,
                    status TEXT NOT NULL,
                    profile TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS doctor_shifts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doctor_id TEXT NOT NULL,
                    weekday INTEGER NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    slot_minutes INTEGER NOT NULL DEFAULT 30,
                    capacity INTEGER NOT NULL DEFAULT 1,
                    UNIQUE (doctor_id, weekday),
                    FOREIGN KEY (doctor_id) REFERENCES doctors(id)
                );

                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    display_name TEXT NOT NULL,
                    doctor_id TEXT,
                    is_demo INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (doctor_id) REFERENCES doctors(id)
                );

                CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_name TEXT NOT NULL,
                    contact_email TEXT,
                    doctor_id TEXT NOT NULL DEFAULT 'amelia-hart',
                    preferred_date TEXT NOT NULL,
                    preferred_time TEXT NOT NULL,
                    appointment_type TEXT NOT NULL,
                    reason TEXT,
                    status TEXT NOT NULL DEFAULT 'Pending Review',
                    conflict INTEGER NOT NULL DEFAULT 0,
                    review_note TEXT,
                    created_by TEXT NOT NULL,
                    created_by_role TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    reviewed_by TEXT,
                    reviewed_role TEXT,
                    reviewed_at TEXT,
                    reschedule_history TEXT NOT NULL DEFAULT '[]',
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    appointment_id INTEGER NOT NULL,
                    actor_username TEXT NOT NULL,
                    actor_role TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (appointment_id) REFERENCES appointments(id)
                );
                """
            )
            _ensure_schema(connection)
            _seed_doctor_schedule(connection)
            _seed_demo_users(connection)

    def _ensure_schema(connection):
        appointment_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(appointments)").fetchall()
        }
        if "doctor_id" not in appointment_columns:
            connection.execute(
                f"ALTER TABLE appointments ADD COLUMN doctor_id TEXT NOT NULL DEFAULT '{DEFAULT_DOCTOR_ID}'"
            )
        if "reschedule_history" not in appointment_columns:
            connection.execute(
                "ALTER TABLE appointments ADD COLUMN reschedule_history TEXT NOT NULL DEFAULT '[]'"
            )
        user_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(users)").fetchall()
        }
        if "doctor_id" not in user_columns:
            connection.execute("ALTER TABLE users ADD COLUMN doctor_id TEXT")
        connection.execute(
            "UPDATE appointments SET doctor_id = ? WHERE doctor_id IS NULL OR doctor_id = ''",
            (DEFAULT_DOCTOR_ID,),
        )

    def _seed_doctor_schedule(connection):
        for doctor in DOCTOR_ROSTER:
            connection.execute(
                """
                INSERT INTO doctors (
                    id, name, department, room, photo, appointment_focus, status, profile
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO NOTHING
                """,
                (
                    doctor["id"],
                    doctor["name"],
                    doctor["department"],
                    doctor["room"],
                    doctor["photo"],
                    doctor["appointment_focus"],
                    doctor["status"],
                    doctor["profile"],
                ),
            )
            for weekday in range(5):
                connection.execute(
                    """
                    INSERT INTO doctor_shifts (
                        doctor_id, weekday, start_time, end_time, slot_minutes, capacity
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(doctor_id, weekday) DO NOTHING
                    """,
                    (
                        doctor["id"],
                        weekday,
                        doctor["start_time"],
                        doctor["end_time"],
                        doctor["slot_minutes"],
                        doctor["capacity"],
                    ),
                )

    def _seed_demo_users(connection):
        seed_time = _now()
        for username, config in DEMO_USERS.items():
            connection.execute(
                """
                INSERT INTO users (
                    username, password_hash, role, display_name, doctor_id, is_demo, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, 1, ?, ?)
                ON CONFLICT(username) DO UPDATE SET
                    password_hash = excluded.password_hash,
                    role = excluded.role,
                    display_name = excluded.display_name,
                    doctor_id = excluded.doctor_id,
                    is_demo = 1,
                    updated_at = excluded.updated_at
                """,
                (
                    username,
                    config["password_hash"],
                    config["role"],
                    config["display_name"],
                    config.get("doctor_id"),
                    seed_time,
                    seed_time,
                ),
            )

    def _json_error(message, status_code=400, details=None):
        payload = {"error": message}
        if details:
            payload["details"] = details
        return jsonify(payload), status_code

    def _parse_payload():
        return request.get_json(silent=True) or {}

    def _find_user(username):
        with _connect() as connection:
            row = connection.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,),
            ).fetchone()
        return dict(row) if row else None

    def _public_user(username):
        user = _find_user(username)
        if not user:
            return None
        return {
            "username": username,
            "role": user["role"],
            "display_name": user["display_name"],
            "doctor_id": user.get("doctor_id"),
            "is_demo": bool(user.get("is_demo", 0)),
        }

    def _current_user():
        user = session.get("user")
        if not user:
            return None
        username = user.get("username")
        stored_user = _public_user(username)
        if not stored_user:
            session.pop("user", None)
            return None
        session["user"] = stored_user
        return stored_user

    def _validate_registration_payload(data):
        username = str(data.get("username", "")).strip().lower()
        password = str(data.get("password", ""))
        confirm_password = str(data.get("confirm_password", password))
        role = str(data.get("role", "")).strip().lower()
        display_name = str(data.get("display_name", "")).strip()

        if not username:
            return None, "username is required"
        if len(username) < 3 or len(username) > 32:
            return None, "username must be 3-32 characters"
        if any(not (char.isalnum() or char in {"_", "-"}) for char in username):
            return None, "username can contain only letters, numbers, underscores, and hyphens"
        if username in DEMO_USERS:
            return None, "demo account usernames are reserved"
        if _find_user(username):
            return None, "username is already registered"
        if not display_name or len(display_name) > 80:
            return None, "display_name is required and must be 80 characters or fewer"
        if role not in REGISTERABLE_ROLES:
            return None, "role must be patient, doctor, or admin"
        if len(password) < 8 or len(password) > 64:
            return None, "password must be 8-64 characters"
        if password != confirm_password:
            return None, "password confirmation does not match"
        return {
            "username": username,
            "password": password,
            "role": role,
            "display_name": display_name,
        }, None

    def _dashboard_endpoint(user):
        if user and user["role"] in STAFF_ROLES:
            return "staff_dashboard"
        return "patient_dashboard"

    def _slugify(value):
        cleaned = []
        for char in str(value).lower():
            cleaned.append(char if char.isalnum() else "-")
        return "-".join(part for part in "".join(cleaned).split("-") if part) or "doctor"

    def _unique_doctor_id(connection, base_value):
        base = _slugify(base_value)
        candidate = base
        suffix = 2
        while connection.execute("SELECT 1 FROM doctors WHERE id = ?", (candidate,)).fetchone():
            candidate = f"{base}-{suffix}"
            suffix += 1
        return candidate

    def _validate_doctor_profile_payload(data, partial=False):
        cleaned = {}
        text_fields = {
            "name": 80,
            "department": 80,
            "room": 80,
            "appointment_focus": 120,
            "status": 40,
            "profile": 240,
        }
        for field, limit in text_fields.items():
            if field in data or not partial:
                value = str(data.get(field, "")).strip()
                if not value:
                    return None, f"{field} is required"
                if len(value) > limit:
                    return None, f"{field} must be {limit} characters or fewer"
                cleaned[field] = value

        if "appointment_focus" in cleaned and cleaned["appointment_focus"] not in APPOINTMENT_TYPES:
            return None, "appointment_focus must be one of the configured appointment booking types"

        for field in ["start_time", "end_time"]:
            if field in data or not partial:
                value = str(data.get(field, "")).strip()
                if not _parse_time(value):
                    return None, f"{field} must use HH:MM 24-hour format"
                cleaned[field] = value

        if {"start_time", "end_time"}.issubset(cleaned):
            if _minutes_from_text(cleaned["start_time"]) >= _minutes_from_text(cleaned["end_time"]):
                return None, "start_time must be earlier than end_time"

        for field, minimum, maximum in [("slot_minutes", 15, 60), ("capacity", 1, 6)]:
            if field in data or not partial:
                try:
                    value = int(data.get(field, SLOT_MINUTES if field == "slot_minutes" else 1))
                except (TypeError, ValueError):
                    return None, f"{field} must be a number"
                if value < minimum or value > maximum:
                    return None, f"{field} must be between {minimum} and {maximum}"
                if field == "slot_minutes" and value not in {15, 30, 60}:
                    return None, "slot_minutes must be 15, 30, or 60"
                cleaned[field] = value

        return cleaned, None

    def _upsert_doctor_profile(connection, doctor_id, profile_data):
        current = connection.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,)).fetchone()
        if not current:
            connection.execute(
                """
                INSERT INTO doctors (
                    id, name, department, room, photo, appointment_focus, status, profile
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    doctor_id,
                    profile_data["name"],
                    profile_data["department"],
                    profile_data["room"],
                    profile_data.get("photo") or f"/api/doctors/{doctor_id}/avatar.svg",
                    profile_data["appointment_focus"],
                    profile_data["status"],
                    profile_data["profile"],
                ),
            )
        else:
            merged = dict(current)
            merged.update({key: value for key, value in profile_data.items() if value is not None})
            connection.execute(
                """
                UPDATE doctors
                SET name = ?, department = ?, room = ?, photo = ?, appointment_focus = ?, status = ?, profile = ?
                WHERE id = ?
                """,
                (
                    merged["name"],
                    merged["department"],
                    merged["room"],
                    merged["photo"],
                    merged["appointment_focus"],
                    merged["status"],
                    merged["profile"],
                    doctor_id,
                ),
            )

        shift_values = {
            "start_time": profile_data.get("start_time"),
            "end_time": profile_data.get("end_time"),
            "slot_minutes": profile_data.get("slot_minutes"),
            "capacity": profile_data.get("capacity"),
        }
        if any(value is not None for value in shift_values.values()):
            existing_shift = connection.execute(
                "SELECT * FROM doctor_shifts WHERE doctor_id = ? AND weekday = 0",
                (doctor_id,),
            ).fetchone()
            defaults = dict(existing_shift) if existing_shift else {
                "start_time": "09:00",
                "end_time": "17:00",
                "slot_minutes": SLOT_MINUTES,
                "capacity": 1,
            }
            defaults.update({key: value for key, value in shift_values.items() if value is not None})
            for weekday in range(5):
                connection.execute(
                    """
                    INSERT INTO doctor_shifts (
                        doctor_id, weekday, start_time, end_time, slot_minutes, capacity
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(doctor_id, weekday) DO UPDATE SET
                        start_time = excluded.start_time,
                        end_time = excluded.end_time,
                        slot_minutes = excluded.slot_minutes,
                        capacity = excluded.capacity
                    """,
                    (
                        doctor_id,
                        weekday,
                        defaults["start_time"],
                        defaults["end_time"],
                        int(defaults["slot_minutes"]),
                        int(defaults["capacity"]),
                    ),
                )

    def _doctor_profile_from_registration(connection, username, display_name):
        doctor_id = _unique_doctor_id(connection, display_name or username)
        return doctor_id, {
            "name": display_name,
            "department": "Appointment Coordination",
            "room": "Consulting Room Pending",
            "appointment_focus": APPOINTMENT_TYPES[0],
            "status": "On duty",
            "profile": "Fictional demo clinician profile created through prototype self-registration.",
            "photo": f"/api/doctors/{doctor_id}/avatar.svg",
            "start_time": "09:00",
            "end_time": "17:00",
            "slot_minutes": SLOT_MINUTES,
            "capacity": 1,
        }

    def _save_uploaded_doctor_photo(doctor_id, uploaded_file):
        filename = secure_filename(uploaded_file.filename or "")
        extension = Path(filename).suffix.lower()
        if extension not in ALLOWED_DOCTOR_PHOTO_EXTENSIONS:
            raise ValueError("photo must be a PNG, JPG, JPEG, or WEBP image")
        image_bytes = uploaded_file.read()
        if not image_bytes:
            raise ValueError("photo file is empty")
        if len(image_bytes) > MAX_DOCTOR_PHOTO_BYTES:
            raise ValueError("photo must be 2 MB or smaller")
        # Keep the prototype simple, but still reject obvious non-image uploads before saving.
        if not (
            image_bytes.startswith(b"\x89PNG")
            or image_bytes.startswith(b"\xff\xd8\xff")
            or image_bytes.startswith(b"RIFF")
        ):
            raise ValueError("photo content must be a valid PNG, JPG, or WEBP image")

        upload_dir = Path(app.config["UPLOAD_FOLDER"])
        upload_dir.mkdir(parents=True, exist_ok=True)
        safe_doctor_id = secure_filename(doctor_id) or "doctor"
        normalized_extension = ".jpg" if extension == ".jpeg" else extension
        # One live photo per doctor keeps the demo tidy and avoids committing runtime uploads.
        for existing in upload_dir.glob(f"{safe_doctor_id}.*"):
            existing.unlink(missing_ok=True)
        target_path = upload_dir / f"{safe_doctor_id}{normalized_extension}"
        target_path.write_bytes(image_bytes)
        return f"uploads/doctors/{target_path.name}"

    def _staff_can_manage_appointment(user, appointment):
        if not user or user["role"] not in STAFF_ROLES:
            return False
        if user["role"] == "admin":
            return True
        if user["role"] == "doctor":
            return bool(user.get("doctor_id")) and appointment.get("doctor_id") == user.get("doctor_id")
        return False

    def _doctor_from_row(row):
        if not row:
            return None
        doctor = dict(row)
        if "shift" not in doctor:
            doctor["shift"] = f"{doctor.get('start_time', '')}-{doctor.get('end_time', '')}"
        return doctor

    def _doctor_by_id(doctor_id):
        if not doctor_id:
            return None
        with _connect() as connection:
            row = connection.execute(
                """
                SELECT d.*, s.start_time, s.end_time, s.slot_minutes, s.capacity
                FROM doctors d
                LEFT JOIN doctor_shifts s
                    ON s.doctor_id = d.id AND s.weekday = 0
                WHERE d.id = ?
                """,
                (doctor_id,),
            ).fetchone()
        return _doctor_from_row(row)

    def _appointment_from_row(row):
        item = dict(row)
        item["conflict"] = bool(item["conflict"])
        try:
            item["reschedule_history"] = json.loads(item.get("reschedule_history") or "[]")
        except json.JSONDecodeError:
            item["reschedule_history"] = []
        item["doctor"] = _doctor_by_id(item.get("doctor_id"))
        return item

    def _audit_from_row(row):
        event = dict(row)
        try:
            event["details"] = json.loads(event["details"])
        except json.JSONDecodeError:
            event["details"] = {}
        return event

    def _write_audit(appointment_id, actor, action, details):
        actor = actor or {"username": "system", "role": "system"}
        with _connect() as connection:
            connection.execute(
                """
                INSERT INTO audit_events (
                    appointment_id, actor_username, actor_role, action, details, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    appointment_id,
                    actor["username"],
                    actor["role"],
                    action,
                    json.dumps(details, sort_keys=True),
                    _now(),
                ),
            )

    def _append_reschedule_history(appointment, actor, details):
        history = list(appointment.get("reschedule_history") or [])
        history.append(
            {
                "actor": actor["username"],
                "role": actor["role"],
                "changed_at": _now(),
                **details,
            }
        )
        return history

    def _find_appointment(appointment_id):
        with _connect() as connection:
            row = connection.execute(
                "SELECT * FROM appointments WHERE id = ?",
                (appointment_id,),
            ).fetchone()
        return _appointment_from_row(row) if row else None

    def _appointment_visible_to_user(appointment):
        user = _current_user()
        if not user:
            return False
        if user["role"] == "admin":
            return True
        if user["role"] == "doctor":
            return bool(user.get("doctor_id")) and appointment.get("doctor_id") == user.get("doctor_id")
        return appointment.get("created_by") == user["username"]

    def _slot_times():
        slots = []
        current_minutes = CLINIC_OPEN_TIME.hour * 60 + CLINIC_OPEN_TIME.minute
        close_minutes = CLINIC_CLOSE_TIME.hour * 60 + CLINIC_CLOSE_TIME.minute
        while current_minutes < close_minutes:
            hour, minute = divmod(current_minutes, 60)
            slots.append(f"{hour:02d}:{minute:02d}")
            current_minutes += SLOT_MINUTES
        return slots

    def _minutes_from_text(value):
        parsed = _parse_time(value)
        if not parsed:
            return None
        return parsed.hour * 60 + parsed.minute

    def _slot_times_for_shift(start_text, end_text, slot_minutes):
        slots = []
        current_minutes = _minutes_from_text(start_text)
        close_minutes = _minutes_from_text(end_text)
        while current_minutes is not None and close_minutes is not None and current_minutes < close_minutes:
            hour, minute = divmod(current_minutes, 60)
            slots.append(f"{hour:02d}:{minute:02d}")
            current_minutes += int(slot_minutes or SLOT_MINUTES)
        return slots

    def _parse_date(value):
        try:
            return datetime.strptime(str(value), "%Y-%m-%d").date()
        except ValueError:
            return None

    def _parse_time(value):
        try:
            return datetime.strptime(str(value), "%H:%M").time()
        except ValueError:
            return None

    def _next_weekday():
        candidate = date.today() + timedelta(days=1)
        while candidate.weekday() >= 5:
            candidate += timedelta(days=1)
        return candidate

    def _validate_business_date(value):
        parsed = _parse_date(value)
        if not parsed:
            return None, "preferred_date must use YYYY-MM-DD format"
        if parsed <= date.today():
            return None, "preferred_date must be a future date"
        if parsed.weekday() >= 5:
            return None, "preferred_date must be a weekday"
        return parsed, None

    def _validate_business_time(value):
        parsed = _parse_time(value)
        if not parsed:
            return None, "preferred_time must use HH:MM 24-hour format"
        if parsed.minute not in {0, 30}:
            return None, "preferred_time must use a 30-minute appointment slot"
        if not (CLINIC_OPEN_TIME <= parsed < CLINIC_CLOSE_TIME):
            return None, "preferred_time must be inside clinic hours from 09:00 to 17:00"
        return parsed, None

    def _validate_appointment_payload(data):
        required = ["patient_name", "preferred_date", "preferred_time", "appointment_type"]
        missing = [field for field in required if not str(data.get(field, "")).strip()]
        if missing:
            return f"Missing required field(s): {', '.join(missing)}"

        _, date_error = _validate_business_date(data["preferred_date"])
        if date_error:
            return date_error

        _, time_error = _validate_business_time(data["preferred_time"])
        if time_error:
            return time_error

        if data["appointment_type"] not in APPOINTMENT_TYPES:
            return "appointment_type must be one of the configured appointment booking types"

        forbidden_terms = [
            "diagnose",
            "diagnosis",
            "prescribe",
            "prescription",
            "treatment plan",
            "medicine advice",
            "medical advice",
        ]
        free_text = " ".join(
            str(data.get(field, "")) for field in ["appointment_type", "reason", "notes"]
        ).lower()
        if any(term in free_text for term in forbidden_terms):
            return "This prototype only handles appointment administration, not diagnosis or treatment advice"

        return None

    def _shift_for_doctor_date(doctor_id, appointment_date):
        if not doctor_id or not appointment_date:
            return None
        with _connect() as connection:
            row = connection.execute(
                """
                SELECT d.id, d.name, d.department, d.room, d.photo, d.appointment_focus,
                       d.status, d.profile, s.start_time, s.end_time, s.slot_minutes, s.capacity
                FROM doctors d
                JOIN doctor_shifts s ON s.doctor_id = d.id
                WHERE d.id = ? AND s.weekday = ?
                """,
                (doctor_id, appointment_date.weekday()),
            ).fetchone()
        return _doctor_from_row(row)

    def _validate_doctor_slot(doctor_id, preferred_date, preferred_time):
        parsed_date = _parse_date(preferred_date)
        parsed_time = _parse_time(preferred_time)
        if not parsed_date or not parsed_time:
            return None, "doctor slot validation requires valid date and time"
        doctor_id = str(doctor_id or DEFAULT_DOCTOR_ID).strip()
        shift = _shift_for_doctor_date(doctor_id, parsed_date)
        if not shift:
            return None, "selected doctor is not scheduled on the selected date"
        if preferred_time not in _slot_times_for_shift(
            shift["start_time"], shift["end_time"], shift["slot_minutes"]
        ):
            return None, "preferred_time must be within the selected doctor's shift"
        return doctor_id, None

    def _resolve_doctor_for_request(data):
        doctor_id = str(data.get("doctor_id", "")).strip() or DEFAULT_DOCTOR_ID
        return _validate_doctor_slot(doctor_id, data.get("preferred_date"), data.get("preferred_time"))

    def _visible_filter(user):
        if user and user["role"] == "patient":
            return "created_by = ?", [user["username"]]
        if user and user["role"] == "doctor":
            if not user.get("doctor_id"):
                return "0 = 1", []
            return "doctor_id = ?", [user["doctor_id"]]
        return "1 = 1", []

    def _refresh_conflicts(actor=None):
        with _connect() as connection:
            before_rows = connection.execute("SELECT id, conflict FROM appointments").fetchall()
            before = {row["id"]: bool(row["conflict"]) for row in before_rows}
            connection.execute("UPDATE appointments SET conflict = 0")
            conflict_slots = connection.execute(
                """
                SELECT doctor_id, preferred_date, preferred_time, COUNT(*) AS occupied_count
                FROM appointments
                WHERE status != 'Cancelled'
                GROUP BY doctor_id, preferred_date, preferred_time
                """
            ).fetchall()
            for slot in conflict_slots:
                parsed_date = _parse_date(slot["preferred_date"])
                shift = connection.execute(
                    """
                    SELECT capacity
                    FROM doctor_shifts
                    WHERE doctor_id = ? AND weekday = ?
                    """,
                    (slot["doctor_id"], parsed_date.weekday() if parsed_date else -1),
                ).fetchone()
                capacity = int(shift["capacity"]) if shift else 1
                if slot["occupied_count"] <= capacity:
                    continue
                connection.execute(
                    """
                    UPDATE appointments
                    SET conflict = 1, updated_at = ?
                    WHERE doctor_id = ? AND preferred_date = ? AND preferred_time = ? AND status != 'Cancelled'
                    """,
                    (_now(), slot["doctor_id"], slot["preferred_date"], slot["preferred_time"]),
                )
            after_rows = connection.execute("SELECT id, conflict FROM appointments").fetchall()
            after = {row["id"]: bool(row["conflict"]) for row in after_rows}

        for appointment_id, new_value in after.items():
            old_value = before.get(appointment_id, False)
            if old_value != new_value:
                _write_audit(
                    appointment_id,
                    actor,
                    "conflict_updated",
                    {"conflict": new_value},
                )

    def _query_appointments(user, filters):
        where_parts = []
        params = []
        visible_sql, visible_params = _visible_filter(user)
        where_parts.append(visible_sql)
        params.extend(visible_params)

        status_filter = filters.get("status")
        if status_filter:
            if status_filter not in STATUS_VALUES:
                raise ValueError("status filter must be Pending Review, Confirmed, or Cancelled")
            where_parts.append("status = ?")
            params.append(status_filter)

        date_filter = filters.get("date")
        if date_filter:
            if not _parse_date(date_filter):
                raise ValueError("date filter must use YYYY-MM-DD format")
            where_parts.append("preferred_date = ?")
            params.append(date_filter)

        query = str(filters.get("q", "")).strip()
        if query:
            like_query = f"%{query.lower()}%"
            where_parts.append(
                """(
                    LOWER(patient_name) LIKE ?
                    OR LOWER(contact_email) LIKE ?
                    OR LOWER(appointment_type) LIKE ?
                    OR LOWER(reason) LIKE ?
                    OR EXISTS (
                        SELECT 1
                        FROM doctors
                        WHERE doctors.id = appointments.doctor_id
                          AND (
                            LOWER(doctors.name) LIKE ?
                            OR LOWER(doctors.department) LIKE ?
                            OR LOWER(doctors.room) LIKE ?
                          )
                    )
                )"""
            )
            params.extend([like_query] * 7)

        page = max(int(filters.get("page", 1) or 1), 1)
        page_size = min(max(int(filters.get("page_size", 10) or 10), 1), 50)
        offset = (page - 1) * page_size
        where_sql = " AND ".join(where_parts)

        with _connect() as connection:
            total = connection.execute(
                f"SELECT COUNT(*) AS total FROM appointments WHERE {where_sql}",
                params,
            ).fetchone()["total"]
            rows = connection.execute(
                f"""
                SELECT *
                FROM appointments
                WHERE {where_sql}
                ORDER BY preferred_date ASC, preferred_time ASC, id DESC
                LIMIT ? OFFSET ?
                """,
                [*params, page_size, offset],
            ).fetchall()

        return {
            "count": total,
            "items": [_appointment_from_row(row) for row in rows],
            "page": page,
            "page_size": page_size,
            "total_pages": max(ceil(total / page_size), 1),
        }

    def _doctor_availability_for_date(doctor_id, date_value, enforce_future=True):
        if enforce_future:
            parsed_date, date_error = _validate_business_date(date_value)
        else:
            parsed_date = _parse_date(date_value)
            date_error = None if parsed_date else "date must use YYYY-MM-DD format"
        if date_error:
            raise ValueError(date_error.replace("preferred_date", "date"))

        shift = _shift_for_doctor_date(doctor_id, parsed_date)
        if not shift:
            raise ValueError("selected doctor is not scheduled on this date")

        slots = {
            slot: {
                "time": slot,
                "available": True,
                "occupied_count": 0,
                "conflict": False,
                "appointment_ids": [],
                "capacity": int(shift["capacity"]),
            }
            for slot in _slot_times_for_shift(shift["start_time"], shift["end_time"], shift["slot_minutes"])
        }
        with _connect() as connection:
            rows = connection.execute(
                """
                SELECT id, preferred_time
                FROM appointments
                WHERE doctor_id = ? AND preferred_date = ? AND status != 'Cancelled'
                """,
                (doctor_id, parsed_date.isoformat()),
            ).fetchall()
        for row in rows:
            slot = slots.get(row["preferred_time"])
            if not slot:
                continue
            slot["occupied_count"] += 1
            slot["appointment_ids"].append(row["id"])
        for slot in slots.values():
            slot["available"] = slot["occupied_count"] < slot["capacity"]
            slot["conflict"] = slot["occupied_count"] > slot["capacity"]
        return {
            "date": parsed_date.isoformat(),
            "doctor": shift,
            "clinic_hours": {
                "open": shift["start_time"],
                "close": shift["end_time"],
                "slot_minutes": int(shift["slot_minutes"]),
            },
            "slots": list(slots.values()),
        }

    def _availability_for_date(date_value):
        return _doctor_availability_for_date(DEFAULT_DOCTOR_ID, date_value, enforce_future=True)

    def _doctors_for_date(date_value, enforce_future=True):
        if enforce_future:
            parsed_date, date_error = _validate_business_date(date_value)
        else:
            parsed_date = _parse_date(date_value)
            date_error = None if parsed_date else "date must use YYYY-MM-DD format"
        if date_error:
            raise ValueError(date_error.replace("preferred_date", "date"))

        with _connect() as connection:
            rows = connection.execute(
                """
                SELECT d.id, d.name, d.department, d.room, d.photo, d.appointment_focus,
                       d.status, d.profile, s.start_time, s.end_time, s.slot_minutes, s.capacity
                FROM doctors d
                JOIN doctor_shifts s ON s.doctor_id = d.id
                WHERE s.weekday = ?
                ORDER BY s.start_time ASC, d.name ASC
                """,
                (parsed_date.weekday(),),
            ).fetchall()

        doctors = []
        for row in rows:
            doctor = _doctor_from_row(row)
            try:
                availability = _doctor_availability_for_date(
                    doctor["id"], parsed_date.isoformat(), enforce_future=enforce_future
                )
                doctor["available_slots"] = sum(1 for slot in availability["slots"] if slot["available"])
                doctor["total_slots"] = len(availability["slots"])
            except ValueError:
                doctor["available_slots"] = 0
                doctor["total_slots"] = 0
            doctors.append(doctor)
        return {
            "service_date": parsed_date.isoformat(),
            "doctors": doctors,
            "safety_boundary": "Fictional demo clinician roster for appointment administration only.",
        }

    def _today_doctors():
        service_date = date.today()
        if service_date.weekday() >= 5:
            service_date = _next_weekday()
        return _doctors_for_date(service_date.isoformat(), enforce_future=False)

    def _schedule_day(date_value, user=None):
        parsed_date = _parse_date(date_value)
        if not parsed_date:
            raise ValueError("date must use YYYY-MM-DD format")
        doctors_payload = _doctors_for_date(parsed_date.isoformat(), enforce_future=False)
        doctor_scope = user.get("doctor_id") if user and user.get("role") == "doctor" else None
        if doctor_scope:
            doctors_payload["doctors"] = [
                doctor for doctor in doctors_payload["doctors"] if doctor["id"] == doctor_scope
            ]
        with _connect() as connection:
            if doctor_scope:
                rows = connection.execute(
                    """
                    SELECT *
                    FROM appointments
                    WHERE preferred_date = ? AND doctor_id = ?
                    ORDER BY preferred_time ASC, id ASC
                    """,
                    (parsed_date.isoformat(), doctor_scope),
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT *
                    FROM appointments
                    WHERE preferred_date = ?
                    ORDER BY preferred_time ASC, id ASC
                    """,
                    (parsed_date.isoformat(),),
                ).fetchall()
        appointments_by_doctor_slot = {}
        for row in rows:
            appointment = _appointment_from_row(row)
            key = (appointment["doctor_id"], appointment["preferred_time"])
            appointments_by_doctor_slot.setdefault(key, []).append(appointment)

        doctor_schedules = []
        for doctor in doctors_payload["doctors"]:
            shift_slots = _slot_times_for_shift(
                doctor["start_time"], doctor["end_time"], doctor["slot_minutes"]
            )
            slots = []
            for slot_time in shift_slots:
                appointments = appointments_by_doctor_slot.get((doctor["id"], slot_time), [])
                active_count = sum(1 for item in appointments if item["status"] != "Cancelled")
                slots.append(
                    {
                        "time": slot_time,
                        "capacity": int(doctor["capacity"]),
                        "occupied_count": active_count,
                        "available": active_count < int(doctor["capacity"]),
                        "conflict": active_count > int(doctor["capacity"]),
                        "appointments": appointments,
                    }
                )
            doctor_schedules.append({"doctor": doctor, "slots": slots})
        return {"date": parsed_date.isoformat(), "doctors": doctor_schedules}

    def _render_login_page():
        demo_accounts = [
            {
                "username": username,
                "password": config["demo_password"],
                "role": config["role"],
                "display_name": config["display_name"],
            }
            for username, config in DEMO_USERS.items()
        ]
        return render_template(
            "login.html",
            demo_accounts=demo_accounts,
            safety_boundary=safety_boundary,
            app_version=APP_VERSION,
        )

    def _render_register_page():
        return render_template(
            "register.html",
            register_roles=["patient", "doctor", "admin"],
            safety_boundary=safety_boundary,
            app_version=APP_VERSION,
        )

    def _require_api_roles(allowed_roles):
        def decorator(view):
            @wraps(view)
            def wrapped(*args, **kwargs):
                user = _current_user()
                if not user:
                    return _json_error("Login required", 401)
                if user["role"] not in allowed_roles:
                    return _json_error("This action requires staff permission", 403)
                return view(*args, **kwargs)

            return wrapped

        return decorator

    def _require_api_login(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not _current_user():
                return _json_error("Login required", 401)
            return view(*args, **kwargs)

        return wrapped

    _init_db()

    @app.get("/")
    def index():
        user = _current_user()
        if not user:
            return _render_login_page()
        return redirect(url_for(_dashboard_endpoint(user)))

    @app.get("/app/login")
    def login_page():
        user = _current_user()
        if user:
            return redirect(url_for(_dashboard_endpoint(user)))
        return _render_login_page()

    @app.get("/login")
    def legacy_login_page():
        return login_page()

    @app.get("/app/register")
    def register_page():
        user = _current_user()
        if user:
            return redirect(url_for(_dashboard_endpoint(user)))
        return _render_register_page()

    @app.get("/register")
    def legacy_register_page():
        return register_page()

    @app.get("/app/patient")
    def patient_dashboard():
        user = _current_user()
        if not user:
            return redirect(url_for("login_page"))
        if user["role"] in STAFF_ROLES:
            return redirect(url_for("staff_dashboard"))
        return render_template(
            "patient.html",
            user=user,
            safety_boundary=safety_boundary,
            appointment_types=APPOINTMENT_TYPES,
            app_version=APP_VERSION,
        )

    @app.get("/patient")
    def legacy_patient_dashboard():
        return patient_dashboard()

    @app.get("/app/staff")
    def staff_dashboard():
        user = _current_user()
        if not user:
            return redirect(url_for("login_page"))
        if user["role"] not in STAFF_ROLES:
            return redirect(url_for("patient_dashboard"))
        return render_template(
            "staff.html",
            user=user,
            safety_boundary=safety_boundary,
            appointment_types=APPOINTMENT_TYPES,
            app_version=APP_VERSION,
        )

    @app.get("/staff")
    def legacy_staff_dashboard():
        return staff_dashboard()

    @app.get("/app/logout")
    def logout_page():
        session.pop("user", None)
        return redirect(url_for("login_page"))

    @app.get("/logout")
    def legacy_logout_page():
        return logout_page()

    @app.get("/health")
    def health():
        return jsonify(
            {
                "status": "ok",
                "service": "clinic-appointment-generator",
                "version": APP_VERSION,
                "storage": "sqlite",
            }
        ), 200

    @app.post("/api/auth/login")
    def api_login():
        data = _parse_payload()
        username = str(data.get("username", "")).strip().lower()
        password = str(data.get("password", ""))

        user_config = _find_user(username)
        if not user_config or not check_password_hash(user_config["password_hash"], password):
            return _json_error("Invalid account credentials", 401)

        user = _public_user(username)
        session["user"] = user
        return jsonify(
            {
                "message": "Login successful",
                "user": user,
                "redirect": url_for(_dashboard_endpoint(user)),
            }
        ), 200

    @app.post("/api/auth/register")
    def api_register():
        data = _parse_payload()
        clean_data, validation_error = _validate_registration_payload(data)
        if validation_error:
            status_code = 409 if "already registered" in validation_error else 400
            return _json_error(validation_error, status_code)

        created_at = _now()
        with _connect() as connection:
            doctor_id = None
            if clean_data["role"] == "doctor":
                doctor_id, doctor_profile = _doctor_profile_from_registration(
                    connection,
                    clean_data["username"],
                    clean_data["display_name"],
                )
                _upsert_doctor_profile(connection, doctor_id, doctor_profile)
            connection.execute(
                """
                INSERT INTO users (
                    username, password_hash, role, display_name, doctor_id, is_demo, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, 0, ?, ?)
                """,
                (
                    clean_data["username"],
                    generate_password_hash(clean_data["password"]),
                    clean_data["role"],
                    clean_data["display_name"],
                    doctor_id,
                    created_at,
                    created_at,
                ),
            )
        user = _public_user(clean_data["username"])
        session["user"] = user
        return jsonify(
            {
                "message": "Registration successful",
                "user": user,
                "redirect": url_for(_dashboard_endpoint(user)),
            }
        ), 201

    @app.post("/api/auth/logout")
    def api_logout():
        session.pop("user", None)
        return jsonify({"message": "Logout successful"}), 200

    @app.get("/api/auth/session")
    def api_session():
        user = _current_user()
        return jsonify({"authenticated": bool(user), "user": user}), 200

    @app.get("/api/availability")
    @_require_api_login
    def availability():
        date_value = request.args.get("date", "")
        if not date_value:
            return _json_error("date query parameter is required", 400)
        doctor_id = request.args.get("doctor_id", DEFAULT_DOCTOR_ID)
        try:
            return jsonify(_doctor_availability_for_date(doctor_id, date_value)), 200
        except ValueError as error:
            return _json_error(str(error), 400)

    @app.get("/api/doctors")
    @_require_api_login
    def doctors_for_date():
        date_value = request.args.get("date") or _next_weekday().isoformat()
        try:
            return jsonify(_doctors_for_date(date_value, enforce_future=True)), 200
        except ValueError as error:
            return _json_error(str(error), 400)

    @app.get("/api/doctors/today")
    @_require_api_login
    def doctors_today():
        return jsonify(_today_doctors()), 200

    @app.get("/api/doctors/<doctor_id>/availability")
    @_require_api_login
    def doctor_availability(doctor_id):
        date_value = request.args.get("date", "")
        if not date_value:
            return _json_error("date query parameter is required", 400)
        try:
            return jsonify(_doctor_availability_for_date(doctor_id, date_value)), 200
        except ValueError as error:
            return _json_error(str(error), 400)

    @app.get("/api/doctors/<doctor_id>/avatar.svg")
    def doctor_avatar(doctor_id):
        doctor = _doctor_by_id(doctor_id)
        if not doctor:
            return _json_error("Doctor not found", 404)
        initials = "".join(
            part[0].upper()
            for part in str(doctor["name"]).split()
            if part and part[0].isascii() and part[0].isalpha()
        )[:2] or "DR"
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="320" height="420" viewBox="0 0 320 420" role="img" aria-label="Fictional doctor profile avatar">
<rect width="320" height="420" fill="#eef8f8"/>
<circle cx="160" cy="140" r="72" fill="#10777f"/>
<rect x="74" y="242" width="172" height="116" rx="20" fill="#ffffff"/>
<rect x="112" y="278" width="96" height="18" rx="9" fill="#d6e4e7"/>
<text x="160" y="166" text-anchor="middle" font-family="Arial, sans-serif" font-size="58" font-weight="700" fill="#ffffff">{initials}</text>
</svg>"""
        return Response(svg, mimetype="image/svg+xml")

    @app.get("/api/doctors/me")
    @_require_api_roles({"doctor"})
    def my_doctor_profile():
        user = _current_user()
        doctor = _doctor_by_id(user.get("doctor_id"))
        if not doctor:
            return _json_error("Doctor profile is not linked to this account", 404)
        return jsonify({"doctor": doctor, "user": user}), 200

    @app.patch("/api/doctors/me")
    @_require_api_roles({"doctor"})
    def update_my_doctor_profile():
        user = _current_user()
        doctor_id = user.get("doctor_id")
        if not doctor_id or not _doctor_by_id(doctor_id):
            return _json_error("Doctor profile is not linked to this account", 404)
        clean_data, validation_error = _validate_doctor_profile_payload(_parse_payload(), partial=True)
        if validation_error:
            return _json_error(validation_error, 400)
        with _connect() as connection:
            _upsert_doctor_profile(connection, doctor_id, clean_data)
            if "name" in clean_data:
                connection.execute(
                    "UPDATE users SET display_name = ?, updated_at = ? WHERE username = ?",
                    (clean_data["name"], _now(), user["username"]),
                )
        _refresh_conflicts(user)
        session["user"] = _public_user(user["username"])
        return jsonify({"message": "Doctor profile updated", "doctor": _doctor_by_id(doctor_id)}), 200

    @app.post("/api/doctors/me/photo")
    @_require_api_roles({"doctor"})
    def upload_my_doctor_photo():
        user = _current_user()
        doctor_id = user.get("doctor_id")
        if not doctor_id or not _doctor_by_id(doctor_id):
            return _json_error("Doctor profile is not linked to this account", 404)
        uploaded_file = request.files.get("photo")
        if not uploaded_file:
            return _json_error("photo file is required", 400)
        try:
            relative_path = _save_uploaded_doctor_photo(doctor_id, uploaded_file)
        except ValueError as error:
            return _json_error(str(error), 400)
        with _connect() as connection:
            _upsert_doctor_profile(connection, doctor_id, {"photo": relative_path})
        return jsonify({"message": "Doctor photo updated", "doctor": _doctor_by_id(doctor_id)}), 200

    @app.get("/api/admin/doctors")
    @_require_api_roles({"admin"})
    def admin_doctors():
        with _connect() as connection:
            rows = connection.execute(
                """
                SELECT d.*, s.start_time, s.end_time, s.slot_minutes, s.capacity,
                       GROUP_CONCAT(u.username) AS linked_usernames
                FROM doctors d
                LEFT JOIN doctor_shifts s ON s.doctor_id = d.id AND s.weekday = 0
                LEFT JOIN users u ON u.doctor_id = d.id
                GROUP BY d.id
                ORDER BY d.name ASC
                """
            ).fetchall()
        doctors = []
        for row in rows:
            doctor = _doctor_from_row(row)
            doctor["linked_usernames"] = [
                username for username in str(row["linked_usernames"] or "").split(",") if username
            ]
            doctors.append(doctor)
        return jsonify({"doctors": doctors}), 200

    @app.post("/api/admin/doctors")
    @_require_api_roles({"admin"})
    def admin_create_doctor():
        data = _parse_payload()
        username = str(data.get("username", "")).strip().lower()
        password = str(data.get("password", ""))
        display_name = str(data.get("display_name", "")).strip() or str(data.get("name", "")).strip()
        if not username:
            return _json_error("username is required", 400)
        if len(username) < 3 or len(username) > 32:
            return _json_error("username must be 3-32 characters", 400)
        if any(not (char.isalnum() or char in {"_", "-"}) for char in username):
            return _json_error("username can contain only letters, numbers, underscores, and hyphens", 400)
        if username in DEMO_USERS or _find_user(username):
            return _json_error("username is already registered", 409)
        if len(password) < 8 or len(password) > 64:
            return _json_error("password must be 8-64 characters", 400)
        if not display_name or len(display_name) > 80:
            return _json_error("display_name is required and must be 80 characters or fewer", 400)

        profile_data, validation_error = _validate_doctor_profile_payload(data, partial=False)
        if validation_error:
            return _json_error(validation_error, 400)
        created_at = _now()
        with _connect() as connection:
            doctor_id = _unique_doctor_id(connection, data.get("doctor_id") or profile_data["name"])
            profile_data["photo"] = f"/api/doctors/{doctor_id}/avatar.svg"
            _upsert_doctor_profile(connection, doctor_id, profile_data)
            connection.execute(
                """
                INSERT INTO users (
                    username, password_hash, role, display_name, doctor_id, is_demo, created_at, updated_at
                )
                VALUES (?, ?, 'doctor', ?, ?, 0, ?, ?)
                """,
                (
                    username,
                    generate_password_hash(password),
                    display_name,
                    doctor_id,
                    created_at,
                    created_at,
                ),
            )
        return jsonify(
            {
                "message": "Doctor account and profile created",
                "doctor": _doctor_by_id(doctor_id),
                "user": _public_user(username),
            }
        ), 201

    @app.patch("/api/admin/doctors/<doctor_id>")
    @_require_api_roles({"admin"})
    def admin_update_doctor(doctor_id):
        if not _doctor_by_id(doctor_id):
            return _json_error("Doctor not found", 404)
        clean_data, validation_error = _validate_doctor_profile_payload(_parse_payload(), partial=True)
        if validation_error:
            return _json_error(validation_error, 400)
        with _connect() as connection:
            _upsert_doctor_profile(connection, doctor_id, clean_data)
        _refresh_conflicts(_current_user())
        return jsonify({"message": "Doctor profile updated", "doctor": _doctor_by_id(doctor_id)}), 200

    @app.get("/api/schedule/day")
    @_require_api_roles(STAFF_ROLES)
    def schedule_day():
        date_value = request.args.get("date") or _next_weekday().isoformat()
        try:
            return jsonify(_schedule_day(date_value, _current_user())), 200
        except ValueError as error:
            return _json_error(str(error), 400)

    @app.post("/api/appointments")
    @_require_api_login
    def create_appointment():
        data = _parse_payload()
        validation_error = _validate_appointment_payload(data)
        if validation_error:
            return _json_error(validation_error, 400)
        doctor_id, doctor_error = _resolve_doctor_for_request(data)
        if doctor_error:
            return _json_error(doctor_error, 400)

        user = _current_user()
        if user["role"] == "doctor" and doctor_id != user.get("doctor_id"):
            return _json_error("Doctor accounts can create requests only for their linked doctor profile", 403)
        created_at = _now()
        with _connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO appointments (
                    patient_name, contact_email, doctor_id, preferred_date, preferred_time,
                    appointment_type, reason, status, conflict, review_note,
                    created_by, created_by_role, created_at, reschedule_history, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending Review', 0, '', ?, ?, ?, '[]', ?)
                """,
                (
                    str(data["patient_name"]).strip(),
                    str(data.get("contact_email", "")).strip(),
                    doctor_id,
                    data["preferred_date"],
                    data["preferred_time"],
                    str(data["appointment_type"]).strip(),
                    str(data.get("reason", "")).strip(),
                    user["username"],
                    user["role"],
                    created_at,
                    created_at,
                ),
            )
            appointment_id = cursor.lastrowid
        _write_audit(
            appointment_id,
            user,
            "created",
            {"status": "Pending Review", "doctor_id": doctor_id},
        )
        _refresh_conflicts(user)
        appointment = _find_appointment(appointment_id)
        return jsonify({"message": "Appointment request created", "appointment": appointment}), 201

    @app.get("/api/appointments")
    @_require_api_login
    def list_appointments():
        try:
            payload = _query_appointments(
                _current_user(),
                {
                    "status": request.args.get("status", ""),
                    "date": request.args.get("date", ""),
                    "q": request.args.get("q", ""),
                    "page": request.args.get("page", 1),
                    "page_size": request.args.get("page_size", 10),
                },
            )
        except ValueError as error:
            return _json_error(str(error), 400)
        return jsonify(payload), 200

    @app.get("/api/appointments/<int:appointment_id>")
    @_require_api_login
    def get_appointment(appointment_id):
        appointment = _find_appointment(appointment_id)
        if not appointment:
            return _json_error("Appointment not found", 404)
        if not _appointment_visible_to_user(appointment):
            return _json_error("Appointment not visible for this account", 403)
        return jsonify({"appointment": appointment}), 200

    @app.patch("/api/appointments/<int:appointment_id>/review")
    @_require_api_roles(STAFF_ROLES)
    def review_appointment(appointment_id):
        appointment = _find_appointment(appointment_id)
        if not appointment:
            return _json_error("Appointment not found", 404)
        user = _current_user()
        if not _staff_can_manage_appointment(user, appointment):
            return _json_error("Doctor accounts can review only their own appointment queue", 403)

        data = _parse_payload()
        status = data.get("status")
        review_note = str(data.get("review_note", "")).strip()
        if status not in STATUS_VALUES:
            return _json_error("status must be Pending Review, Confirmed, or Cancelled", 400)
        if not review_note:
            return _json_error("review_note is required for staff review actions", 400)

        reviewed_at = _now()
        with _connect() as connection:
            connection.execute(
                """
                UPDATE appointments
                SET status = ?, review_note = ?, reviewed_by = ?, reviewed_role = ?,
                    reviewed_at = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    status,
                    review_note,
                    user["display_name"],
                    user["role"],
                    reviewed_at,
                    reviewed_at,
                    appointment_id,
                ),
            )
        _write_audit(appointment_id, user, "reviewed", {"status": status, "review_note": review_note})
        _refresh_conflicts(user)
        return jsonify({"message": "Appointment reviewed", "appointment": _find_appointment(appointment_id)}), 200

    @app.patch("/api/appointments/<int:appointment_id>/cancel")
    @_require_api_login
    def cancel_appointment(appointment_id):
        appointment = _find_appointment(appointment_id)
        if not appointment:
            return _json_error("Appointment not found", 404)
        user = _current_user()
        if user["role"] != "patient" or appointment.get("created_by") != user["username"]:
            return _json_error("Only the patient who created this request can cancel it here", 403)
        if appointment["status"] == "Cancelled":
            return _json_error("Appointment is already cancelled", 400)

        data = _parse_payload()
        note = str(data.get("reason", "Cancelled by patient request.")).strip() or "Cancelled by patient request."
        updated_at = _now()
        with _connect() as connection:
            connection.execute(
                """
                UPDATE appointments
                SET status = 'Cancelled', review_note = ?, updated_at = ?
                WHERE id = ?
                """,
                (note, updated_at, appointment_id),
            )
        _write_audit(appointment_id, user, "patient_cancelled", {"reason": note})
        _refresh_conflicts(user)
        return jsonify({"message": "Appointment cancelled", "appointment": _find_appointment(appointment_id)}), 200

    @app.patch("/api/appointments/<int:appointment_id>/reschedule")
    @_require_api_login
    def reschedule_appointment(appointment_id):
        appointment = _find_appointment(appointment_id)
        if not appointment:
            return _json_error("Appointment not found", 404)
        if appointment["status"] == "Cancelled":
            return _json_error("Cancelled appointments cannot be rescheduled", 400)

        user = _current_user()
        is_staff = user["role"] in STAFF_ROLES
        if not is_staff and appointment.get("created_by") != user["username"]:
            return _json_error("Only staff or the patient who created this request can reschedule it", 403)
        if is_staff and not _staff_can_manage_appointment(user, appointment):
            return _json_error("Doctor accounts can reschedule only their own appointment queue", 403)
        if not is_staff and appointment["status"] != "Pending Review":
            return _json_error("Patients can reschedule only requests that are still Pending Review", 400)

        data = _parse_payload()
        reschedule_payload = {
            "patient_name": appointment["patient_name"],
            "preferred_date": data.get("preferred_date"),
            "preferred_time": data.get("preferred_time"),
            "appointment_type": appointment["appointment_type"],
            "reason": appointment.get("reason", ""),
            "doctor_id": data.get("doctor_id") or appointment.get("doctor_id"),
        }
        validation_error = _validate_appointment_payload(reschedule_payload)
        if validation_error:
            return _json_error(validation_error, 400)
        doctor_id, doctor_error = _resolve_doctor_for_request(reschedule_payload)
        if doctor_error:
            return _json_error(doctor_error, 400)
        if is_staff and user["role"] == "doctor" and doctor_id != user.get("doctor_id"):
            return _json_error("Doctor accounts can move appointments only within their linked doctor profile", 403)

        review_note = str(data.get("review_note", "")).strip()
        if is_staff and not review_note:
            return _json_error("review_note is required for staff reschedule actions", 400)
        if not review_note:
            review_note = "Patient requested appointment reschedule."

        updated_at = _now()
        history = _append_reschedule_history(
            appointment,
            user,
            {
                "from": {
                    "doctor_id": appointment.get("doctor_id"),
                    "preferred_date": appointment["preferred_date"],
                    "preferred_time": appointment["preferred_time"],
                },
                "to": {
                    "doctor_id": doctor_id,
                    "preferred_date": reschedule_payload["preferred_date"],
                    "preferred_time": reschedule_payload["preferred_time"],
                },
                "review_note": review_note,
            },
        )
        with _connect() as connection:
            connection.execute(
                """
                UPDATE appointments
                SET doctor_id = ?, preferred_date = ?, preferred_time = ?,
                    review_note = ?, reschedule_history = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    doctor_id,
                    reschedule_payload["preferred_date"],
                    reschedule_payload["preferred_time"],
                    review_note,
                    json.dumps(history, sort_keys=True),
                    updated_at,
                    appointment_id,
                ),
            )
        _write_audit(
            appointment_id,
            user,
            "rescheduled",
            {
                "doctor_id": doctor_id,
                "preferred_date": reschedule_payload["preferred_date"],
                "preferred_time": reschedule_payload["preferred_time"],
                "review_note": review_note,
            },
        )
        _refresh_conflicts(user)
        return jsonify({"message": "Appointment rescheduled", "appointment": _find_appointment(appointment_id)}), 200

    @app.get("/api/appointments/<int:appointment_id>/audit")
    @_require_api_roles(STAFF_ROLES)
    def appointment_audit(appointment_id):
        appointment = _find_appointment(appointment_id)
        if not appointment:
            return _json_error("Appointment not found", 404)
        if not _staff_can_manage_appointment(_current_user(), appointment):
            return _json_error("Doctor accounts can view audit events only for their own appointment queue", 403)
        with _connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM audit_events
                WHERE appointment_id = ?
                ORDER BY id ASC
                """,
                (appointment_id,),
            ).fetchall()
        return jsonify({"appointment_id": appointment_id, "events": [_audit_from_row(row) for row in rows]}), 200

    @app.get("/api/appointments/<int:appointment_id>/summary")
    @_require_api_login
    def appointment_summary(appointment_id):
        appointment = _find_appointment(appointment_id)
        if not appointment:
            return _json_error("Appointment not found", 404)
        if not _appointment_visible_to_user(appointment):
            return _json_error("Appointment not visible for this account", 403)

        summary = (
            f"Administrative summary: {appointment['patient_name']} requested a "
            f"{appointment['appointment_type']} appointment on {appointment['preferred_date']} "
            f"at {appointment['preferred_time']} with "
            f"{appointment.get('doctor', {}).get('name', 'the assigned doctor')}. "
            f"Current status: {appointment['status']}. "
            "This summary is non-diagnostic and does not provide treatment advice."
        )
        return jsonify({"summary": summary, "safety_boundary": safety_boundary}), 200

    @app.get("/api/meta/requirements")
    def meta_requirements():
        return jsonify(
            {
                "business_problem": "Clinic staff need a safe prototype to collect, review, and coordinate appointment requests.",
                "requirements": requirements_summary,
                "demo_roles": [
                    {"username": username, "role": config["role"], "display_name": config["display_name"]}
                    for username, config in DEMO_USERS.items()
                ],
                "doctor_roster": _today_doctors()["doctors"],
                "closed_loop_endpoints": [
                    "GET /api/doctors/me",
                    "PATCH /api/doctors/me",
                    "GET /api/admin/doctors",
                    "POST /api/admin/doctors",
                    "GET /api/doctors?date=YYYY-MM-DD",
                    "GET /api/doctors/<doctor_id>/availability?date=YYYY-MM-DD",
                    "GET /api/schedule/day?date=YYYY-MM-DD",
                    "PATCH /api/appointments/<id>/reschedule",
                ],
                "auth_endpoints": [
                    "POST /api/auth/register",
                    "POST /api/auth/login",
                    "POST /api/auth/logout",
                    "GET /api/auth/session",
                ],
                "app_version": APP_VERSION,
                "storage": "SQLite",
                "safety_boundary": safety_boundary,
            }
        ), 200

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not Found", "message": "The requested resource does not exist"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal Server Error", "message": "Unexpected server error"}), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
