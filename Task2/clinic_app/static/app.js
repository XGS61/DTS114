const form = document.querySelector("#appointmentForm");
const formMessage = document.querySelector("#formMessage");
const appointmentList = document.querySelector("#appointmentList");
const refreshButton = document.querySelector("#refreshButton");

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

function statusClass(status) {
  return status.toLowerCase().replace(/\s+/g, "-");
}

function renderAppointment(item) {
  const card = document.createElement("article");
  card.className = "appointment-card";
  card.innerHTML = `
    <header>
      <div>
        <strong>#${item.id} ${item.patient_name}</strong>
        <div>${item.preferred_date} at ${item.preferred_time}</div>
      </div>
      <span class="status ${statusClass(item.status)}">${item.status}</span>
    </header>
    <div><strong>Type:</strong> ${item.appointment_type}</div>
    <div><strong>Reason:</strong> ${item.reason || "Not provided"}</div>
    ${item.conflict ? '<div class="conflict">Conflict flagged: another active request uses this slot.</div>' : ""}
    ${item.review_note ? `<div><strong>Review note:</strong> ${item.review_note}</div>` : ""}
    <div class="actions">
      <button type="button" data-action="summary" data-id="${item.id}" class="secondary">Summary</button>
      <button type="button" data-action="confirm" data-id="${item.id}">Confirm</button>
      <button type="button" data-action="cancel" data-id="${item.id}" class="secondary">Cancel</button>
    </div>
    <div class="summary" id="summary-${item.id}" hidden></div>
  `;
  return card;
}

async function loadAppointments() {
  appointmentList.innerHTML = "Loading appointments...";
  try {
    const payload = await api("/api/appointments");
    appointmentList.innerHTML = "";
    if (payload.items.length === 0) {
      appointmentList.textContent = "No appointment requests yet.";
      return;
    }
    payload.items.forEach((item) => appointmentList.appendChild(renderAppointment(item)));
  } catch (error) {
    appointmentList.textContent = error.message;
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  formMessage.textContent = "Submitting...";
  const data = Object.fromEntries(new FormData(form).entries());
  try {
    const payload = await api("/api/appointments", {
      method: "POST",
      body: JSON.stringify(data)
    });
    formMessage.textContent = payload.appointment.conflict
      ? "Request submitted. Conflict flagged for receptionist review."
      : "Request submitted for receptionist review.";
    form.reset();
    await loadAppointments();
  } catch (error) {
    formMessage.textContent = error.message;
  }
});

appointmentList.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;

  const id = button.dataset.id;
  const action = button.dataset.action;
  try {
    if (action === "summary") {
      const payload = await api(`/api/appointments/${id}/summary`);
      const summary = document.querySelector(`#summary-${id}`);
      summary.textContent = payload.summary;
      summary.hidden = false;
      return;
    }

    const status = action === "confirm" ? "Confirmed" : "Cancelled";
    await api(`/api/appointments/${id}/review`, {
      method: "PATCH",
      body: JSON.stringify({
        status,
        review_note: `Receptionist marked this request as ${status}.`
      })
    });
    await loadAppointments();
  } catch (error) {
    formMessage.textContent = error.message;
  }
});

refreshButton.addEventListener("click", loadAppointments);
loadAppointments();
