const loginForm = document.querySelector("#loginForm");
const appointmentForm = document.querySelector("#appointmentForm");
const formMessage = document.querySelector("#formMessage");
const loginMessage = document.querySelector("#loginMessage");
const patientAppointmentList = document.querySelector("#patientAppointmentList");
const staffAppointmentList = document.querySelector("#staffAppointmentList");
const refreshButton = document.querySelector("#refreshButton");
const statusFilter = document.querySelector("#statusFilter");
const weatherForm = document.querySelector("#weatherForm");
const weatherResult = document.querySelector("#weatherResult");

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || payload.message || "Request failed");
  }
  return payload;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function statusClass(status) {
  return String(status || "unknown").toLowerCase().replace(/[^a-z0-9]+/g, "-");
}

async function performLogin(username, password) {
  const payload = await api("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password })
  });
  window.location.assign(payload.redirect);
}

function renderPatientAppointment(item) {
  const card = document.createElement("article");
  card.className = "appointment-card";
  card.innerHTML = `
    <header>
      <div>
        <strong>#${escapeHtml(item.id)} ${escapeHtml(item.patient_name)}</strong>
        <div>${escapeHtml(item.preferred_date)} at ${escapeHtml(item.preferred_time)}</div>
      </div>
      <span class="status ${statusClass(item.status)}">${escapeHtml(item.status)}</span>
    </header>
    <div><strong>Type:</strong> ${escapeHtml(item.appointment_type)}</div>
    <div><strong>Reason:</strong> ${escapeHtml(item.reason || "Not provided")}</div>
    ${item.conflict ? '<div class="conflict">Conflict flagged: clinic staff will review this slot.</div>' : ""}
    ${item.review_note ? `<div><strong>Review note:</strong> ${escapeHtml(item.review_note)}</div>` : ""}
    <div class="actions">
      <button type="button" data-action="summary" data-id="${escapeHtml(item.id)}" class="secondary">Summary</button>
    </div>
    <div class="summary" id="summary-${escapeHtml(item.id)}" hidden></div>
  `;
  return card;
}

function renderStaffAppointment(item) {
  const card = document.createElement("article");
  card.className = "appointment-card staff-card";
  card.innerHTML = `
    <header>
      <div>
        <strong>#${escapeHtml(item.id)} ${escapeHtml(item.patient_name)}</strong>
        <div>${escapeHtml(item.preferred_date)} at ${escapeHtml(item.preferred_time)}</div>
      </div>
      <span class="status ${statusClass(item.status)}">${escapeHtml(item.status)}</span>
    </header>
    <div class="card-grid">
      <div><strong>Type:</strong> ${escapeHtml(item.appointment_type)}</div>
      <div><strong>Created by:</strong> ${escapeHtml(item.created_by || "unknown")}</div>
      <div><strong>Email:</strong> ${escapeHtml(item.contact_email || "Not provided")}</div>
      <div><strong>Created:</strong> ${escapeHtml(item.created_at || "Not recorded")}</div>
    </div>
    <div><strong>Reason:</strong> ${escapeHtml(item.reason || "Not provided")}</div>
    ${item.conflict ? '<div class="conflict">Conflict flagged: another active request uses this slot.</div>' : ""}
    ${item.review_note ? `<div><strong>Review note:</strong> ${escapeHtml(item.review_note)}</div>` : ""}
    <div class="actions">
      <button type="button" data-action="summary" data-id="${escapeHtml(item.id)}" class="secondary">Summary</button>
      <button type="button" data-action="confirm" data-id="${escapeHtml(item.id)}">Confirm</button>
      <button type="button" data-action="cancel" data-id="${escapeHtml(item.id)}" class="secondary danger">Cancel</button>
      <button type="button" data-action="reopen" data-id="${escapeHtml(item.id)}" class="secondary">Reopen</button>
    </div>
    <div class="summary" id="summary-${escapeHtml(item.id)}" hidden></div>
  `;
  return card;
}

async function loadAppointments() {
  const list = staffAppointmentList || patientAppointmentList;
  if (!list) return;

  list.innerHTML = "Loading appointments...";
  const query = staffAppointmentList && statusFilter && statusFilter.value
    ? `?status=${encodeURIComponent(statusFilter.value)}`
    : "";

  try {
    const payload = await api(`/api/appointments${query}`);
    list.innerHTML = "";
    if (payload.items.length === 0) {
      list.textContent = staffAppointmentList
        ? "No appointment requests match this view."
        : "No appointment requests yet.";
      return;
    }
    payload.items.forEach((item) => {
      list.appendChild(staffAppointmentList ? renderStaffAppointment(item) : renderPatientAppointment(item));
    });
  } catch (error) {
    list.textContent = error.message;
  }
}

async function showSummary(id) {
  const payload = await api(`/api/appointments/${id}/summary`);
  const summary = document.querySelector(`#summary-${id}`);
  summary.textContent = payload.summary;
  summary.hidden = false;
}

async function reviewAppointment(id, status) {
  const defaultNote = status === "Confirmed"
    ? "Appointment slot confirmed by clinic staff."
    : status === "Cancelled"
      ? "Appointment request cancelled by clinic staff."
      : "Appointment request returned to pending review.";
  const reviewNote = window.prompt("Review note", defaultNote) || defaultNote;
  await api(`/api/appointments/${id}/review`, {
    method: "PATCH",
    body: JSON.stringify({ status, review_note: reviewNote })
  });
  await loadAppointments();
}

if (loginForm) {
  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    loginMessage.textContent = "Signing in...";
    const data = Object.fromEntries(new FormData(loginForm).entries());
    try {
      await performLogin(data.username, data.password);
    } catch (error) {
      loginMessage.textContent = error.message;
    }
  });

  document.querySelectorAll("[data-demo-login]").forEach((button) => {
    button.addEventListener("click", async () => {
      loginMessage.textContent = "Signing in...";
      try {
        await performLogin(button.dataset.username, button.dataset.password);
      } catch (error) {
        loginMessage.textContent = error.message;
      }
    });
  });
}

if (appointmentForm) {
  appointmentForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    formMessage.textContent = "Submitting...";
    const data = Object.fromEntries(new FormData(appointmentForm).entries());
    try {
      const payload = await api("/api/appointments", {
        method: "POST",
        body: JSON.stringify(data)
      });
      formMessage.textContent = payload.appointment.conflict
        ? "Request submitted. Conflict flagged for staff review."
        : "Request submitted for staff review.";
      appointmentForm.reset();
      await loadAppointments();
    } catch (error) {
      formMessage.textContent = error.message;
    }
  });
}

const activeAppointmentList = staffAppointmentList || patientAppointmentList;
if (activeAppointmentList) {
  activeAppointmentList.addEventListener("click", async (event) => {
    const button = event.target.closest("button[data-action]");
    if (!button) return;

    try {
      const id = button.dataset.id;
      const action = button.dataset.action;
      if (action === "summary") {
        await showSummary(id);
      } else if (action === "confirm") {
        await reviewAppointment(id, "Confirmed");
      } else if (action === "cancel") {
        await reviewAppointment(id, "Cancelled");
      } else if (action === "reopen") {
        await reviewAppointment(id, "Pending Review");
      }
    } catch (error) {
      const target = formMessage || activeAppointmentList;
      target.textContent = error.message;
    }
  });
}

if (refreshButton) {
  refreshButton.addEventListener("click", loadAppointments);
}

if (statusFilter) {
  statusFilter.addEventListener("change", loadAppointments);
}

if (weatherForm) {
  weatherForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    weatherResult.textContent = "Checking weather...";
    const data = Object.fromEntries(new FormData(weatherForm).entries());
    try {
      const payload = await api(`/api/clinic/weather?city=${encodeURIComponent(data.city)}`);
      weatherResult.textContent = payload.available
        ? `${payload.city}: ${payload.temperature_c} C, ${payload.condition}. ${payload.safe_use}`
        : `${payload.city}: ${payload.message} ${payload.safe_use}`;
    } catch (error) {
      weatherResult.textContent = error.message;
    }
  });
}

loadAppointments();
