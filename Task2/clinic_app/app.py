from datetime import UTC, datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request


BASE_DIR = Path(__file__).resolve().parent


def create_app(test_config=None):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.update(test_config or {})

    appointments = []
    next_id = {"value": 1}

    safety_boundary = {
        "scope": "Appointment administration prototype only",
        "not_allowed": [
            "diagnosis",
            "treatment advice",
            "prescriptions",
            "real patient records",
        ],
        "human_review": "Receptionist must confirm or cancel each appointment request.",
    }

    requirements_summary = {
        "methodology": "AI-DLC-informed iterative methodology",
        "inception": [
            "Define clinic appointment administration problem",
            "Identify actors: Patient, Receptionist, Clinic System",
            "Set safety boundary: no diagnosis, no treatment advice, no real patient records",
        ],
        "construction": [
            "Generate requirements, user stories, UML source, Flask API, website, and image",
            "Validate generated artefacts against safety and workflow checklist",
        ],
        "operations": [
            "Use Git commits for traceability",
            "Run tests through CI/CD",
            "Deploy the Flask website/API",
        ],
    }

    def _json_error(message, status_code=400, details=None):
        payload = {"error": message}
        if details:
            payload["details"] = details
        return jsonify(payload), status_code

    def _parse_payload():
        return request.get_json(silent=True) or {}

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

    def _has_conflict(preferred_date, preferred_time):
        return any(
            item["preferred_date"] == preferred_date
            and item["preferred_time"] == preferred_time
            and item["status"] != "Cancelled"
            for item in appointments
        )

    @app.get("/")
    def index():
        return render_template("index.html", safety_boundary=safety_boundary)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "clinic-appointment-generator"}), 200

    @app.post("/api/appointments")
    def create_appointment():
        data = _parse_payload()
        validation_error = _validate_appointment_payload(data)
        if validation_error:
            return _json_error(validation_error, 400)

        conflict = _has_conflict(data["preferred_date"], data["preferred_time"])
        appointment = {
            "id": next_id["value"],
            "patient_name": str(data["patient_name"]).strip(),
            "contact_email": str(data.get("contact_email", "")).strip(),
            "preferred_date": data["preferred_date"],
            "preferred_time": data["preferred_time"],
            "appointment_type": str(data["appointment_type"]).strip(),
            "reason": str(data.get("reason", "")).strip(),
            "status": "Pending Review",
            "conflict": conflict,
            "review_note": "",
            "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        }
        appointments.append(appointment)
        next_id["value"] += 1

        return jsonify({"message": "Appointment request created", "appointment": appointment}), 201

    @app.get("/api/appointments")
    def list_appointments():
        status_filter = request.args.get("status")
        if status_filter:
            filtered = [item for item in appointments if item["status"] == status_filter]
        else:
            filtered = appointments
        return jsonify({"count": len(filtered), "items": filtered}), 200

    @app.get("/api/appointments/<int:appointment_id>")
    def get_appointment(appointment_id):
        appointment = next((item for item in appointments if item["id"] == appointment_id), None)
        if not appointment:
            return _json_error("Appointment not found", 404)
        return jsonify({"appointment": appointment}), 200

    @app.patch("/api/appointments/<int:appointment_id>/review")
    def review_appointment(appointment_id):
        appointment = next((item for item in appointments if item["id"] == appointment_id), None)
        if not appointment:
            return _json_error("Appointment not found", 404)

        data = _parse_payload()
        status = data.get("status")
        if status not in {"Confirmed", "Cancelled"}:
            return _json_error("status must be either Confirmed or Cancelled", 400)

        appointment["status"] = status
        appointment["review_note"] = str(data.get("review_note", "")).strip()
        appointment["reviewed_at"] = datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
        return jsonify({"message": "Appointment reviewed", "appointment": appointment}), 200

    @app.get("/api/appointments/<int:appointment_id>/summary")
    def appointment_summary(appointment_id):
        appointment = next((item for item in appointments if item["id"] == appointment_id), None)
        if not appointment:
            return _json_error("Appointment not found", 404)

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
                "business_problem": "Clinic staff need a safe prototype to collect and review appointment requests.",
                "requirements": requirements_summary,
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
