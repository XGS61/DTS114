import json
import os
from datetime import UTC, datetime
from functools import wraps
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, session, url_for


BASE_DIR = Path(__file__).resolve().parent
STAFF_ROLES = {"doctor", "admin", "receptionist"}

DEMO_USERS = {
    "patient": {
        "password": "patient123",
        "role": "patient",
        "display_name": "Demo Patient",
    },
    "doctor": {
        "password": "doctor123",
        "role": "doctor",
        "display_name": "Dr Morgan",
    },
    "admin": {
        "password": "admin123",
        "role": "admin",
        "display_name": "Clinic Admin",
    },
}


def create_app(test_config=None):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_mapping(
        SECRET_KEY=os.getenv("FLASK_SECRET_KEY", "dts114-demo-secret"),
        DATA_FILE=BASE_DIR / "data" / "appointments.json",
    )
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
            "Generate requirements, user stories, UML source, Flask API, role-based website, and image",
            "Validate generated artefacts against safety, role, workflow, and testing checklists",
        ],
        "operations": [
            "Use Git commits for traceability",
            "Run tests through CI/CD",
            "Deploy the Flask website/API with environment-variable based configuration",
        ],
        "ai_specific_tooling": [
            "Prompt templates and structured JSON artefacts in the notebook",
            "DeepSeek API support for SDLC artefact generation with recorded metadata",
            "Deterministic fallback when API keys are not configured",
            "Submission validation script for structure, metadata, language, and secret checks",
        ],
    }

    def _json_error(message, status_code=400, details=None):
        payload = {"error": message}
        if details:
            payload["details"] = details
        return jsonify(payload), status_code

    def _parse_payload():
        return request.get_json(silent=True) or {}

    def _data_file():
        return Path(app.config["DATA_FILE"])

    def _load_appointments():
        path = _data_file()
        if not path.exists():
            return []
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []

    def _save_appointments():
        path = _data_file()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(appointments, indent=2), encoding="utf-8")

    appointments = _load_appointments()

    def _next_id():
        return max((int(item.get("id", 0)) for item in appointments), default=0) + 1

    def _public_user(username):
        user = DEMO_USERS[username]
        return {
            "username": username,
            "role": user["role"],
            "display_name": user["display_name"],
        }

    def _current_user():
        user = session.get("user")
        if not user:
            return None
        username = user.get("username")
        if username not in DEMO_USERS:
            session.pop("user", None)
            return None
        return user

    def _dashboard_endpoint(user):
        if user and user["role"] in STAFF_ROLES:
            return "staff_dashboard"
        return "patient_dashboard"

    def _render_login_page():
        demo_accounts = [
            {
                "username": username,
                "password": config["password"],
                "role": config["role"],
                "display_name": config["display_name"],
            }
            for username, config in DEMO_USERS.items()
        ]
        return render_template(
            "login.html",
            demo_accounts=demo_accounts,
            safety_boundary=safety_boundary,
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

    def _validate_appointment_payload(data):
        required = ["patient_name", "preferred_date", "preferred_time", "appointment_type"]
        missing = [field for field in required if not str(data.get(field, "")).strip()]
        if missing:
            return f"Missing required field(s): {', '.join(missing)}"

        try:
            datetime.strptime(data["preferred_date"], "%Y-%m-%d")
        except ValueError:
            return "preferred_date must use YYYY-MM-DD format"

        try:
            datetime.strptime(data["preferred_time"], "%H:%M")
        except ValueError:
            return "preferred_time must use HH:MM 24-hour format"

        forbidden_terms = ["diagnose", "diagnosis", "prescribe", "prescription", "treatment plan"]
        free_text = " ".join(
            str(data.get(field, "")) for field in ["appointment_type", "reason", "notes"]
        ).lower()
        if any(term in free_text for term in forbidden_terms):
            return "This prototype only handles appointment administration, not diagnosis or treatment advice"

        return None

    def _has_conflict(preferred_date, preferred_time, excluded_id=None):
        return any(
            item["preferred_date"] == preferred_date
            and item["preferred_time"] == preferred_time
            and item["status"] != "Cancelled"
            and item["id"] != excluded_id
            for item in appointments
        )

    def _find_appointment(appointment_id):
        return next((item for item in appointments if item["id"] == appointment_id), None)

    def _refresh_conflicts():
        active_slots = {}
        for item in appointments:
            if item["status"] == "Cancelled":
                continue
            key = (item["preferred_date"], item["preferred_time"])
            active_slots.setdefault(key, []).append(item["id"])

        for item in appointments:
            key = (item["preferred_date"], item["preferred_time"])
            item["conflict"] = item["status"] != "Cancelled" and len(active_slots.get(key, [])) > 1

    def _visible_appointments():
        user = _current_user()
        if user and user["role"] == "patient":
            return [item for item in appointments if item.get("created_by") == user["username"]]
        return appointments

    def _appointment_visible_to_user(appointment):
        user = _current_user()
        if not user:
            return False
        if user["role"] in STAFF_ROLES:
            return True
        return appointment.get("created_by") == user["username"]

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
        return jsonify({"status": "ok", "service": "clinic-appointment-generator"}), 200

    @app.post("/api/auth/login")
    def api_login():
        data = _parse_payload()
        username = str(data.get("username", "")).strip().lower()
        password = str(data.get("password", ""))

        user_config = DEMO_USERS.get(username)
        if not user_config or user_config["password"] != password:
            return _json_error("Invalid demo account credentials", 401)

        user = _public_user(username)
        session["user"] = user
        return jsonify(
            {
                "message": "Login successful",
                "user": user,
                "redirect": url_for(_dashboard_endpoint(user)),
            }
        ), 200

    @app.post("/api/auth/logout")
    def api_logout():
        session.pop("user", None)
        return jsonify({"message": "Logout successful"}), 200

    @app.get("/api/auth/session")
    def api_session():
        user = _current_user()
        return jsonify({"authenticated": bool(user), "user": user}), 200

    @app.post("/api/appointments")
    @_require_api_login
    def create_appointment():
        data = _parse_payload()
        validation_error = _validate_appointment_payload(data)
        if validation_error:
            return _json_error(validation_error, 400)

        user = _current_user()
        appointment = {
            "id": _next_id(),
            "patient_name": str(data["patient_name"]).strip(),
            "contact_email": str(data.get("contact_email", "")).strip(),
            "preferred_date": data["preferred_date"],
            "preferred_time": data["preferred_time"],
            "appointment_type": str(data["appointment_type"]).strip(),
            "reason": str(data.get("reason", "")).strip(),
            "status": "Pending Review",
            "conflict": False,
            "review_note": "",
            "created_by": user["username"],
            "created_by_role": user["role"],
            "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        }
        appointments.append(appointment)
        _refresh_conflicts()
        _save_appointments()

        return jsonify({"message": "Appointment request created", "appointment": appointment}), 201

    @app.get("/api/appointments")
    @_require_api_login
    def list_appointments():
        status_filter = request.args.get("status")
        visible_items = _visible_appointments()
        if status_filter:
            visible_items = [item for item in visible_items if item["status"] == status_filter]
        return jsonify({"count": len(visible_items), "items": visible_items}), 200

    @app.get("/api/appointments/<int:appointment_id>")
    @_require_api_login
    def get_appointment(appointment_id):
        appointment = _find_appointment(appointment_id)
        if not appointment:
            return _json_error("Appointment not found", 404)
        if not _appointment_visible_to_user(appointment):
            return _json_error("Appointment not visible for this patient account", 403)
        return jsonify({"appointment": appointment}), 200

    @app.patch("/api/appointments/<int:appointment_id>/review")
    @_require_api_roles(STAFF_ROLES)
    def review_appointment(appointment_id):
        appointment = _find_appointment(appointment_id)
        if not appointment:
            return _json_error("Appointment not found", 404)

        data = _parse_payload()
        status = data.get("status")
        if status not in {"Pending Review", "Confirmed", "Cancelled"}:
            return _json_error("status must be Pending Review, Confirmed, or Cancelled", 400)

        user = _current_user()
        appointment["status"] = status
        appointment["review_note"] = str(data.get("review_note", "")).strip()
        appointment["reviewed_by"] = user["display_name"]
        appointment["reviewed_role"] = user["role"]
        appointment["reviewed_at"] = datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
        _refresh_conflicts()
        _save_appointments()
        return jsonify({"message": "Appointment reviewed", "appointment": appointment}), 200

    @app.get("/api/appointments/<int:appointment_id>/summary")
    @_require_api_login
    def appointment_summary(appointment_id):
        appointment = _find_appointment(appointment_id)
        if not appointment:
            return _json_error("Appointment not found", 404)
        if not _appointment_visible_to_user(appointment):
            return _json_error("Appointment not visible for this patient account", 403)

        summary = (
            f"Administrative summary: {appointment['patient_name']} requested a "
            f"{appointment['appointment_type']} appointment on {appointment['preferred_date']} "
            f"at {appointment['preferred_time']}. Current status: {appointment['status']}. "
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
