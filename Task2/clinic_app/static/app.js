const pageName = document.body.dataset.page || "";

const loginForm = document.querySelector("#loginForm");
const registerForm = document.querySelector("#registerForm");
const appointmentForm = document.querySelector("#appointmentForm");
const reviewForm = document.querySelector("#reviewForm");
const rescheduleForm = document.querySelector("#rescheduleForm");
const doctorProfileForm = document.querySelector("#doctorProfileForm");
const doctorPhotoForm = document.querySelector("#doctorPhotoForm");
const doctorPhotoInput = document.querySelector("#doctorPhotoInput");
const doctorPhotoChoose = document.querySelector("#doctorPhotoChoose");
const doctorPhotoFileName = document.querySelector("#doctorPhotoFileName");
const adminDoctorForm = document.querySelector("#adminDoctorForm");
const formMessage = document.querySelector("#formMessage");
const loginMessage = document.querySelector("#loginMessage");
const registerMessage = document.querySelector("#registerMessage");
const reviewMessage = document.querySelector("#reviewMessage");
const rescheduleMessage = document.querySelector("#rescheduleMessage");
const doctorProfileMessage = document.querySelector("#doctorProfileMessage");
const doctorPhotoMessage = document.querySelector("#doctorPhotoMessage");
const adminDoctorMessage = document.querySelector("#adminDoctorMessage");
const patientAppointmentList = document.querySelector("#patientAppointmentList");
const staffAppointmentList = document.querySelector("#staffAppointmentList");
const refreshButton = document.querySelector("#refreshButton");
const statusFilter = document.querySelector("#statusFilter");
const patientStatusFilter = document.querySelector("#patientStatusFilter");
const patientSearch = document.querySelector("#patientSearch");
const staffSearch = document.querySelector("#staffSearch");
const staffDateFilter = document.querySelector("#staffDateFilter");
const scheduleDateFilter = document.querySelector("#scheduleDateFilter");
const scheduleRefreshButton = document.querySelector("#scheduleRefreshButton");
const patientPrevPage = document.querySelector("#patientPrevPage");
const patientNextPage = document.querySelector("#patientNextPage");
const patientPageInfo = document.querySelector("#patientPageInfo");
const staffPrevPage = document.querySelector("#staffPrevPage");
const staffNextPage = document.querySelector("#staffNextPage");
const staffPageInfo = document.querySelector("#staffPageInfo");
const pendingMetric = document.querySelector("#pendingMetric");
const confirmedMetric = document.querySelector("#confirmedMetric");
const cancelledMetric = document.querySelector("#cancelledMetric");
const conflictMetric = document.querySelector("#conflictMetric");
const todayMetric = document.querySelector("#todayMetric");
const datePickers = document.querySelectorAll("[data-date-picker]");
const dateInput = document.querySelector("[name='preferred_date']");
const timeInput = document.querySelector("[name='preferred_time']");
const doctorSelect = document.querySelector("#doctorSelect");
const bookingSummary = document.querySelector("#bookingSummary");
const availabilityMessage = document.querySelector("#availabilityMessage");
const availabilitySlots = document.querySelector("#availabilitySlots");
const doctorRosterMessage = document.querySelector("#doctorRosterMessage");
const doctorRosterList = document.querySelector("#doctorRosterList");
const doctorRosterSearch = document.querySelector("#doctorRosterSearch");
const doctorProfilePhoto = document.querySelector("#doctorProfilePhoto");
const scheduleDayBoard = document.querySelector("#scheduleDayBoard");
const adminDoctorList = document.querySelector("#adminDoctorList");
const detailDrawer = document.querySelector("#detailDrawer");
const drawerTitle = document.querySelector("#drawerTitle");
const drawerContent = document.querySelector("#drawerContent");
const reviewModal = document.querySelector("#reviewModal");
const rescheduleModal = document.querySelector("#rescheduleModal");
const currentUserRole = document.body.dataset.userRole || "";
const currentDoctorId = document.body.dataset.doctorId || "";
const workspaceHeaderTitle = document.querySelector(".workspace-header h1");
const workspaceHeaderLead = document.querySelector(".workspace-header .lead");
const workspaceViewLinks = document.querySelectorAll("[data-view-target]");
const workspaceViews = document.querySelectorAll("[data-workspace-view]");

const MONTH_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"
];

const appointmentState = {
  patientPage: 1,
  staffPage: 1,
  pageSize: 8,
  selectedAppointmentId: null,
  selectedDoctorId: "",
  currentDetail: null,
  doctors: []
};

function formatDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function parseDate(value) {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value || "");
  if (!match) return null;
  const date = new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]));
  return Number.isNaN(date.getTime()) ? null : date;
}

function nextWeekday(fromDate = new Date()) {
  const candidate = new Date(fromDate);
  candidate.setDate(candidate.getDate() + 1);
  while (candidate.getDay() === 0 || candidate.getDay() === 6) {
    candidate.setDate(candidate.getDate() + 1);
  }
  return candidate;
}

function dispatchDateChange(input) {
  input.dispatchEvent(new Event("change", { bubbles: true }));
}

function isSelectableBusinessDate(date) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const candidate = new Date(date);
  candidate.setHours(0, 0, 0, 0);
  return candidate > today && candidate.getDay() !== 0 && candidate.getDay() !== 6;
}

function setupDatePicker(picker) {
  const input = picker.querySelector("[data-date-input]");
  const toggle = picker.querySelector("[data-date-toggle]");
  const popover = picker.querySelector("[data-calendar-popover]");
  const title = picker.querySelector("[data-calendar-title]");
  const grid = picker.querySelector("[data-calendar-grid]");
  const previous = picker.querySelector("[data-calendar-prev]");
  const next = picker.querySelector("[data-calendar-next]");
  const clear = picker.querySelector("[data-calendar-clear]");
  const today = picker.querySelector("[data-calendar-today]");
  let viewDate = parseDate(input.value) || nextWeekday();

  function closeCalendar() {
    popover.hidden = true;
  }

  function openCalendar() {
    renderCalendar();
    popover.hidden = false;
  }

  function renderCalendar() {
    const year = viewDate.getFullYear();
    const month = viewDate.getMonth();
    const selected = parseDate(input.value);
    const firstOfMonth = new Date(year, month, 1);
    const start = new Date(year, month, 1 - firstOfMonth.getDay());
    title.textContent = `${MONTH_NAMES[month]} ${year}`;
    grid.innerHTML = "";

    for (let index = 0; index < 42; index += 1) {
      const cellDate = new Date(start);
      cellDate.setDate(start.getDate() + index);
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = String(cellDate.getDate());
      button.dataset.dateValue = formatDate(cellDate);
      button.setAttribute("role", "gridcell");
      button.setAttribute("aria-label", `${MONTH_NAMES[cellDate.getMonth()]} ${cellDate.getDate()}, ${cellDate.getFullYear()}`);
      if (cellDate.getMonth() !== month) button.classList.add("is-outside");
      if (selected && formatDate(cellDate) === formatDate(selected)) button.classList.add("is-selected");
      if (!isSelectableBusinessDate(cellDate)) {
        button.classList.add("is-disabled");
        button.disabled = true;
      }
      grid.appendChild(button);
    }
  }

  toggle.addEventListener("click", () => {
    if (popover.hidden) openCalendar();
    else closeCalendar();
  });

  input.addEventListener("click", openCalendar);

  input.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeCalendar();
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      openCalendar();
    }
  });

  previous.addEventListener("click", () => {
    viewDate = new Date(viewDate.getFullYear(), viewDate.getMonth() - 1, 1);
    renderCalendar();
  });

  next.addEventListener("click", () => {
    viewDate = new Date(viewDate.getFullYear(), viewDate.getMonth() + 1, 1);
    renderCalendar();
  });

  today.addEventListener("click", () => {
    const candidate = nextWeekday();
    input.value = formatDate(candidate);
    viewDate = candidate;
    renderCalendar();
    closeCalendar();
    dispatchDateChange(input);
  });

  clear.addEventListener("click", () => {
    input.value = "";
    closeCalendar();
    dispatchDateChange(input);
  });

  grid.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-date-value]");
    if (!button || button.disabled) return;
    input.value = button.dataset.dateValue;
    viewDate = parseDate(input.value) || viewDate;
    closeCalendar();
    input.focus();
    dispatchDateChange(input);
  });

  document.addEventListener("click", (event) => {
    if (!picker.contains(event.target)) closeCalendar();
  });
}

datePickers.forEach(setupDatePicker);

function activateWorkspaceView(viewName, updateUrl = true) {
  if (!workspaceViews.length || !viewName) return;
  const target = document.querySelector(`[data-workspace-view="${CSS.escape(viewName)}"]`);
  if (!target) return;
  workspaceViews.forEach((view) => {
    const isActive = view === target;
    view.classList.toggle("is-active", isActive);
    view.hidden = !isActive;
  });
  workspaceViewLinks.forEach((link) => {
    const isActive = link.dataset.viewTarget === viewName;
    link.classList.toggle("is-active", isActive);
    if (isActive) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
  if (workspaceHeaderTitle && target.dataset.viewTitle) {
    workspaceHeaderTitle.textContent = target.dataset.viewTitle;
  }
  if (workspaceHeaderLead && target.dataset.viewLead) {
    workspaceHeaderLead.textContent = target.dataset.viewLead;
  }
  if (updateUrl) {
    window.history.replaceState(null, "", `#${viewName}`);
  }
}

function setupWorkspaceViews() {
  if (!workspaceViews.length) return;
  workspaceViewLinks.forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      activateWorkspaceView(link.dataset.viewTarget);
    });
  });
  const initialView = (window.location.hash || "").replace("#", "")
    || document.querySelector("[data-workspace-view].is-active")?.dataset.workspaceView
    || workspaceViews[0]?.dataset.workspaceView;
  activateWorkspaceView(initialView, false);
}

setupWorkspaceViews();

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

async function uploadApi(path, formData) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Accept": "application/json" },
    body: formData
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || payload.message || "Upload failed");
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

function assetUrl(path) {
  const value = String(path || "");
  if (value.startsWith("/")) return value;
  return `/static/${value}`;
}

function statusClass(status) {
  return String(status || "unknown").toLowerCase().replace(/[^a-z0-9]+/g, "-");
}

function setMessage(target, message, state = "") {
  if (!target) return;
  target.className = state ? `message ${state}` : "message";
  target.textContent = message;
}

function renderState(container, message, className) {
  container.innerHTML = `<div class="${className}">${escapeHtml(message)}</div>`;
}

function parseTimeToMinutes(value) {
  const match = /^(\d{2}):(\d{2})$/.exec(value || "");
  if (!match) return null;
  return Number(match[1]) * 60 + Number(match[2]);
}

function formatMinutesAsTime(totalMinutes) {
  const hours = String(Math.floor(totalMinutes / 60)).padStart(2, "0");
  const minutes = String(totalMinutes % 60).padStart(2, "0");
  return `${hours}:${minutes}`;
}

function previewDoctorTimes(doctor) {
  const start = parseTimeToMinutes(doctor.start_time);
  const end = parseTimeToMinutes(doctor.end_time);
  const step = Number(doctor.slot_minutes || 30);
  if (start === null || end === null || step <= 0) return [];
  const times = [];
  for (let minutes = start; minutes < end && times.length < 4; minutes += step) {
    times.push(formatMinutesAsTime(minutes));
  }
  return times;
}

function buildQuery(params) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && String(value).trim() !== "") {
      query.set(key, value);
    }
  });
  const text = query.toString();
  return text ? `?${text}` : "";
}

function doctorLabel(item) {
  return item?.doctor?.name || item?.doctor_id || "Assigned doctor";
}

function updateBookingSummary() {
  if (!bookingSummary) return;
  const selectedDoctor = doctorSelect?.selectedOptions?.[0]?.textContent || "";
  const dateValue = dateInput?.value || "";
  const timeValue = timeInput?.value || "";
  if (!dateValue || !selectedDoctor || !timeValue) {
    bookingSummary.textContent = "Select a future weekday, doctor, and available slot.";
    return;
  }
  bookingSummary.textContent = `Selected booking: ${selectedDoctor} on ${dateValue} at ${timeValue}.`;
}

async function performLogin(username, password) {
  const payload = await api("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password })
  });
  window.location.assign(payload.redirect);
}

async function performRegistration(data) {
  const payload = await api("/api/auth/register", {
    method: "POST",
    body: JSON.stringify(data)
  });
  window.location.assign(payload.redirect);
}

function appointmentHeader(item) {
  return `
    <header>
      <div>
        <strong>#${escapeHtml(item.id)} ${escapeHtml(item.patient_name)}</strong>
        <div class="muted">${escapeHtml(item.preferred_date)} at ${escapeHtml(item.preferred_time)}</div>
      </div>
      <span class="status ${statusClass(item.status)}">${escapeHtml(item.status)}</span>
    </header>
  `;
}

function appointmentMeta(item) {
  return `
    <div class="meta-row">
      <span class="meta-pill">${escapeHtml(item.appointment_type)}</span>
      <span class="meta-pill">${escapeHtml(doctorLabel(item))}</span>
      <span class="meta-pill">Created by ${escapeHtml(item.created_by || "unknown")}</span>
      ${item.conflict ? '<span class="meta-pill">Conflict flagged</span>' : ""}
    </div>
  `;
}

function renderPatientAppointment(item) {
  const card = document.createElement("article");
  card.className = "appointment-card";
  card.innerHTML = `
    ${appointmentHeader(item)}
    ${appointmentMeta(item)}
    <div><strong>Reason:</strong> ${escapeHtml(item.reason || "Not provided")}</div>
    ${item.conflict ? '<div class="conflict">Conflict flagged: clinic staff will review this slot.</div>' : ""}
    ${item.review_note ? `<div><strong>Review note:</strong> ${escapeHtml(item.review_note)}</div>` : ""}
    <div class="actions">
      <button type="button" data-action="summary" data-id="${escapeHtml(item.id)}" class="secondary">Summary</button>
      ${item.status === "Pending Review" ? `<button type="button" data-action="patient-reschedule" data-id="${escapeHtml(item.id)}" class="secondary">Use Selected Slot to Reschedule</button>` : ""}
      ${item.status !== "Cancelled" ? `<button type="button" data-action="patient-cancel" data-id="${escapeHtml(item.id)}" class="secondary danger">Cancel Request</button>` : ""}
    </div>
    <div class="summary" id="summary-${escapeHtml(item.id)}" hidden></div>
  `;
  return card;
}

function renderStaffAppointment(item) {
  const card = document.createElement("article");
  card.className = `appointment-card staff-card ${appointmentState.selectedAppointmentId === item.id ? "is-active" : ""}`;
  card.innerHTML = `
    ${appointmentHeader(item)}
    ${appointmentMeta(item)}
    <div class="card-grid">
      <div><strong>Email:</strong> ${escapeHtml(item.contact_email || "Not provided")}</div>
      <div><strong>Created:</strong> ${escapeHtml(item.created_at || "Not recorded")}</div>
    </div>
    <div><strong>Reason:</strong> ${escapeHtml(item.reason || "Not provided")}</div>
    ${item.conflict ? '<div class="conflict">Conflict flagged: another active request uses this slot.</div>' : ""}
    <div class="actions">
      <button type="button" data-action="open-detail" data-id="${escapeHtml(item.id)}">Open Detail</button>
      <button type="button" data-action="summary" data-id="${escapeHtml(item.id)}" class="secondary">Summary</button>
    </div>
    <div class="summary" id="summary-${escapeHtml(item.id)}" hidden></div>
  `;
  return card;
}

function updatePaginationControls(payload, isStaff) {
  const previous = isStaff ? staffPrevPage : patientPrevPage;
  const next = isStaff ? staffNextPage : patientNextPage;
  const info = isStaff ? staffPageInfo : patientPageInfo;
  if (!previous || !next || !info) return;
  previous.disabled = payload.page <= 1;
  next.disabled = payload.page >= payload.total_pages;
  info.textContent = `Page ${payload.page} of ${payload.total_pages}`;
}

async function updateStaffMetrics() {
  if (!pendingMetric) return;
  try {
    const payload = await api("/api/appointments?page_size=50");
    const today = formatDate(new Date());
    const counts = payload.items.reduce((summary, item) => {
      summary[item.status] = (summary[item.status] || 0) + 1;
      summary.conflicts += item.conflict ? 1 : 0;
      summary.today += item.preferred_date === today ? 1 : 0;
      return summary;
    }, { conflicts: 0, today: 0 });
    pendingMetric.textContent = counts["Pending Review"] || 0;
    confirmedMetric.textContent = counts.Confirmed || 0;
    cancelledMetric.textContent = counts.Cancelled || 0;
    conflictMetric.textContent = counts.conflicts || 0;
    todayMetric.textContent = counts.today || 0;
  } catch (error) {
    pendingMetric.textContent = "!";
  }
}

function collectListParams(isStaff) {
  if (isStaff) {
    return {
      status: statusFilter?.value || "",
      date: staffDateFilter?.value || "",
      q: staffSearch?.value || "",
      page: appointmentState.staffPage,
      page_size: appointmentState.pageSize
    };
  }
  return {
    status: patientStatusFilter?.value || "",
    q: patientSearch?.value || "",
    page: appointmentState.patientPage,
    page_size: appointmentState.pageSize
  };
}

async function loadAppointments() {
  const list = staffAppointmentList || patientAppointmentList;
  if (!list) return;
  const isStaff = Boolean(staffAppointmentList);
  renderState(list, "Loading appointments...", "loading-state");

  try {
    const payload = await api(`/api/appointments${buildQuery(collectListParams(isStaff))}`);
    list.innerHTML = "";
    updatePaginationControls(payload, isStaff);
    if (payload.items.length === 0) {
      renderState(list, isStaff ? "No appointment requests match this view." : "No appointment requests yet.", "empty-state");
      if (isStaff) await updateStaffMetrics();
      return;
    }
    payload.items.forEach((item) => {
      list.appendChild(isStaff ? renderStaffAppointment(item) : renderPatientAppointment(item));
    });
    if (isStaff) await updateStaffMetrics();
  } catch (error) {
    renderState(list, error.message, "error-state");
  }
}

async function loadAvailability(dateValue) {
  if (!availabilitySlots || !availabilityMessage) return;
  availabilitySlots.innerHTML = "";
  if (!dateValue) {
    setMessage(availabilityMessage, "Select a future weekday to preview clinic slots.");
    updateBookingSummary();
    return;
  }
  const selectedDoctorId = doctorSelect?.value || "";
  if (doctorSelect && !selectedDoctorId) {
    setMessage(availabilityMessage, "Select a doctor to preview available slots.");
    updateBookingSummary();
    return;
  }

  setMessage(availabilityMessage, "Loading available slots...");
  try {
    const path = selectedDoctorId
      ? `/api/doctors/${encodeURIComponent(selectedDoctorId)}/availability${buildQuery({ date: dateValue })}`
      : `/api/availability${buildQuery({ date: dateValue })}`;
    const payload = await api(path);
    const openSlots = payload.slots.filter((slot) => slot.available).length;
    setMessage(
      availabilityMessage,
      `${openSlots} available slots for ${doctorLabel(payload)} on ${payload.date}. Clinic hours: ${payload.clinic_hours.open}-${payload.clinic_hours.close}.`
    );
    payload.slots.forEach((slot) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "slot-button";
      button.textContent = `${slot.time} (${slot.occupied_count}/${slot.capacity})`;
      button.dataset.slotTime = slot.time;
      if (!slot.available) button.classList.add("is-occupied");
      if (slot.conflict) button.classList.add("is-conflict");
      button.title = slot.available ? "Select this appointment slot" : "Occupied slot";
      availabilitySlots.appendChild(button);
    });
  } catch (error) {
    setMessage(availabilityMessage, error.message, "error");
  }
  updateBookingSummary();
}

function renderDoctorCard(doctor) {
  const card = document.createElement("article");
  card.className = "doctor-card";
  card.dataset.doctorId = doctor.id;
  const selectedDate = dateInput?.value || "Select date";
  const previewTimes = previewDoctorTimes(doctor);
  const availabilityLabel = `${doctor.available_slots ?? "Not loaded"} of ${doctor.total_slots ?? "not loaded"} slots`;
  card.innerHTML = `
    <img src="${escapeHtml(assetUrl(doctor.photo))}" alt="${escapeHtml(doctor.name)} profile image">
    <div class="doctor-card-body doctor-identity">
      <span>${escapeHtml(doctor.department)}</span>
      <div>
        <strong>${escapeHtml(doctor.name)}</strong>
        <span class="status confirmed">${escapeHtml(doctor.status)}</span>
      </div>
      <p>${escapeHtml(doctor.profile || doctor.appointment_focus)}</p>
      <dl>
        <div><dt>Shift</dt><dd>${escapeHtml(doctor.shift)}</dd></div>
        <div><dt>Room</dt><dd>${escapeHtml(doctor.room)}</dd></div>
        <div><dt>Booking Focus</dt><dd>${escapeHtml(doctor.appointment_focus)}</dd></div>
      </dl>
    </div>
    <div class="doctor-slot-panel">
      <div class="date-chip-row">
        <span class="date-chip is-active">${escapeHtml(selectedDate)}</span>
        <span class="date-chip">${escapeHtml(doctor.shift)}</span>
        <span class="date-chip is-muted">${escapeHtml(availabilityLabel)}</span>
      </div>
      <div class="time-chip-row" aria-label="Doctor shift preview">
        ${previewTimes.length ? previewTimes.map((time, index) => `<span class="time-chip ${index === 0 ? "is-active" : ""}">${escapeHtml(time)}</span>`).join("") : '<span class="time-chip is-muted">No shift preview</span>'}
      </div>
      <button type="button" class="secondary" data-select-doctor="${escapeHtml(doctor.id)}">Select Doctor</button>
    </div>
  `;
  return card;
}

function doctorMatchesSearch(doctor, query) {
  if (!query) return true;
  const haystack = [
    doctor.name,
    doctor.department,
    doctor.room,
    doctor.appointment_focus,
    doctor.profile
  ].join(" ").toLowerCase();
  return haystack.includes(query.toLowerCase());
}

function renderDoctorRoster(doctors) {
  if (!doctorRosterList) return;
  const query = doctorRosterSearch?.value.trim() || "";
  const visibleDoctors = doctors.filter((doctor) => doctorMatchesSearch(doctor, query));
  doctorRosterList.innerHTML = "";
  if (!visibleDoctors.length) {
    renderState(doctorRosterList, "No doctors match this search.", "empty-state");
    return;
  }
  visibleDoctors.forEach((doctor) => {
    doctorRosterList.appendChild(renderDoctorCard(doctor));
  });
  doctorRosterList.querySelectorAll(".doctor-card").forEach((card) => {
    card.classList.toggle("is-selected", card.dataset.doctorId === doctorSelect?.value);
  });
}

function populateDoctorSelect(doctors) {
  if (!doctorSelect) return;
  const previousValue = doctorSelect.value || appointmentState.selectedDoctorId;
  doctorSelect.innerHTML = '<option value="">Select doctor</option>';
  doctors.forEach((doctor) => {
    const option = document.createElement("option");
    option.value = doctor.id;
    option.textContent = `${doctor.name} | ${doctor.department} | ${doctor.shift}`;
    doctorSelect.appendChild(option);
  });
  const candidate = doctors.find((doctor) => doctor.id === previousValue) || doctors[0];
  if (candidate) {
    doctorSelect.value = candidate.id;
    appointmentState.selectedDoctorId = candidate.id;
  }
}

async function loadDoctorRoster(dateValue = "") {
  if (!doctorRosterList || !doctorRosterMessage) return;
  doctorRosterList.innerHTML = "";
  setMessage(doctorRosterMessage, dateValue ? "Loading doctors for selected date..." : "Loading today's roster...");
  try {
    const payload = dateValue
      ? await api(`/api/doctors${buildQuery({ date: dateValue })}`)
      : await api("/api/doctors/today");
    setMessage(
      doctorRosterMessage,
      `${payload.doctors.length} doctors available for ${payload.service_date}.`
    );
    appointmentState.doctors = payload.doctors;
    populateDoctorSelect(payload.doctors);
    renderDoctorRoster(payload.doctors);
    await loadAvailability(dateInput?.value || "");
  } catch (error) {
    setMessage(doctorRosterMessage, error.message, "error");
    if (doctorSelect) doctorSelect.innerHTML = '<option value="">No doctors available</option>';
  }
  updateBookingSummary();
}

async function showSummary(id) {
  const payload = await api(`/api/appointments/${id}/summary`);
  const summary = document.querySelector(`#summary-${id}`);
  if (!summary) return;
  summary.textContent = payload.summary;
  summary.hidden = false;
}

async function cancelPatientAppointment(id) {
  const reason = window.prompt("Cancellation reason", "Cancelled by patient request.") || "Cancelled by patient request.";
  await api(`/api/appointments/${id}/cancel`, {
    method: "PATCH",
    body: JSON.stringify({ reason })
  });
  await loadAppointments();
}

async function reschedulePatientAppointment(id) {
  if (!appointmentForm || !dateInput || !timeInput || !doctorSelect) return;
  const data = Object.fromEntries(new FormData(appointmentForm).entries());
  if (!data.preferred_date || !data.preferred_time || !data.doctor_id) {
    setMessage(formMessage, "Select a future weekday, doctor, and slot above before rescheduling.", "error");
    return;
  }
  await api(`/api/appointments/${id}/reschedule`, {
    method: "PATCH",
    body: JSON.stringify({
      doctor_id: data.doctor_id,
      preferred_date: data.preferred_date,
      preferred_time: data.preferred_time,
      review_note: "Patient requested appointment reschedule."
    })
  });
  setMessage(formMessage, "Reschedule request saved for staff review.");
  await loadAppointments();
  await loadAvailability(data.preferred_date);
}

function renderDetail(appointment, summary, auditEvents) {
  drawerTitle.textContent = `Request #${appointment.id}`;
  appointmentState.currentDetail = appointment;
  drawerContent.innerHTML = `
    <div class="detail-grid">
      <div class="detail-item"><span>Patient</span>${escapeHtml(appointment.patient_name)}</div>
      <div class="detail-item"><span>Status</span>${escapeHtml(appointment.status)}</div>
      <div class="detail-item"><span>Doctor</span>${escapeHtml(doctorLabel(appointment))}</div>
      <div class="detail-item"><span>Room</span>${escapeHtml(appointment.doctor?.room || "Not assigned")}</div>
      <div class="detail-item"><span>Date</span>${escapeHtml(appointment.preferred_date)}</div>
      <div class="detail-item"><span>Time</span>${escapeHtml(appointment.preferred_time)}</div>
      <div class="detail-item"><span>Type</span>${escapeHtml(appointment.appointment_type)}</div>
      <div class="detail-item"><span>Conflict</span>${appointment.conflict ? "Yes" : "No"}</div>
      <div class="detail-item"><span>Email</span>${escapeHtml(appointment.contact_email || "Not provided")}</div>
      <div class="detail-item"><span>Created By</span>${escapeHtml(appointment.created_by || "unknown")}</div>
    </div>
    <section>
      <h3>Administrative Reason</h3>
      <p>${escapeHtml(appointment.reason || "Not provided")}</p>
    </section>
    <section>
      <h3>Non-Diagnostic Summary</h3>
      <p>${escapeHtml(summary)}</p>
    </section>
    <section>
      <h3>Audit Timeline</h3>
      <div class="audit-list">
        ${auditEvents.length ? auditEvents.map((event) => `
          <div class="audit-event">
            <span>${escapeHtml(event.action)} | ${escapeHtml(event.created_at)}</span>
            <strong>${escapeHtml(event.actor_username)} (${escapeHtml(event.actor_role)})</strong>
            <p>${escapeHtml(JSON.stringify(event.details))}</p>
          </div>
        `).join("") : '<div class="empty-state">No audit events recorded.</div>'}
      </div>
    </section>
    <section>
      <h3>Reschedule History</h3>
      <div class="audit-list">
        ${appointment.reschedule_history?.length ? appointment.reschedule_history.map((event) => `
          <div class="audit-event">
            <span>${escapeHtml(event.changed_at)} | ${escapeHtml(event.actor)} (${escapeHtml(event.role)})</span>
            <p>${escapeHtml(JSON.stringify(event.to))}</p>
          </div>
        `).join("") : '<div class="empty-state">No reschedule events recorded.</div>'}
      </div>
    </section>
  `;
}

async function openDetailDrawer(id) {
  appointmentState.selectedAppointmentId = Number(id);
  detailDrawer.hidden = false;
  drawerContent.innerHTML = '<div class="loading-state">Loading appointment detail...</div>';
  try {
    const appointmentPayload = await api(`/api/appointments/${id}`);
    const summaryPayload = await api(`/api/appointments/${id}/summary`);
    const auditPayload = await api(`/api/appointments/${id}/audit`);
    renderDetail(appointmentPayload.appointment, summaryPayload.summary, auditPayload.events);
    await loadAppointments();
  } catch (error) {
    drawerContent.innerHTML = `<div class="error-state">${escapeHtml(error.message)}</div>`;
  }
}

function closeDetailDrawer() {
  if (!detailDrawer) return;
  detailDrawer.hidden = true;
  appointmentState.selectedAppointmentId = null;
}

function openReviewModal(status) {
  if (!reviewModal || !reviewForm || !appointmentState.selectedAppointmentId) return;
  reviewForm.appointment_id.value = String(appointmentState.selectedAppointmentId);
  reviewForm.status.value = status;
  reviewForm.decision_label.value = status;
  reviewForm.review_note.value = status === "Confirmed"
    ? "Appointment slot confirmed by clinic staff."
    : status === "Cancelled"
      ? "Appointment request cancelled after staff review."
      : "Appointment request returned to pending review for further checking.";
  setMessage(reviewMessage, "");
  reviewModal.hidden = false;
}

function closeReviewModal() {
  if (reviewModal) reviewModal.hidden = true;
}

function renderScheduleDay(payload) {
  if (!scheduleDayBoard) return;
  if (!payload.doctors.length) {
    renderState(scheduleDayBoard, "No doctors are scheduled for this date.", "empty-state");
    return;
  }
  const times = [...new Set(payload.doctors.flatMap((entry) => entry.slots.map((slot) => slot.time)))].sort();
  const doctorHeaders = payload.doctors.map((entry) => `
    <div class="schedule-cell schedule-doctor-header">
      <img src="${escapeHtml(assetUrl(entry.doctor.photo))}" alt="${escapeHtml(entry.doctor.name)} profile image">
      <div>
        <strong>${escapeHtml(entry.doctor.name)}</strong>
        <span>${escapeHtml(entry.doctor.department)}</span>
        <small>${escapeHtml(entry.doctor.room)} | ${escapeHtml(entry.doctor.shift)}</small>
      </div>
    </div>
  `).join("");

  const rows = times.map((time) => `
    <div class="schedule-cell schedule-time-cell">${escapeHtml(time)}</div>
    ${payload.doctors.map((entry) => {
      const slot = entry.slots.find((candidate) => candidate.time === time);
      if (!slot) {
        return '<div class="schedule-cell schedule-empty">Outside shift</div>';
      }
      return `
        <div class="schedule-cell schedule-slot-cell ${slot.conflict ? "is-conflict" : slot.available ? "is-open" : "is-full"}">
          <div class="capacity-line">
            <span>${escapeHtml(slot.occupied_count)} / ${escapeHtml(slot.capacity)}</span>
            <span>${slot.available ? "Open" : "Full"}</span>
          </div>
          ${slot.appointments.length ? slot.appointments.map((appointment) => `
            <button type="button" data-action="open-detail" data-id="${escapeHtml(appointment.id)}" class="schedule-appointment appointment-block-${statusClass(appointment.status)}">
              <strong>#${escapeHtml(appointment.id)} ${escapeHtml(appointment.patient_name)}</strong>
              <span>${escapeHtml(appointment.appointment_type)} | ${escapeHtml(appointment.status)}</span>
            </button>
          `).join("") : '<span class="muted">Available</span>'}
        </div>
      `;
    }).join("")}
  `).join("");

  scheduleDayBoard.innerHTML = `
    <div class="schedule-table" style="--doctor-columns: ${payload.doctors.length}">
      <div class="schedule-cell schedule-time-header">Time</div>
      ${doctorHeaders}
      ${rows}
    </div>
  `;
}

async function loadScheduleDay() {
  if (!scheduleDayBoard) return;
  if (scheduleDateFilter && !scheduleDateFilter.value) {
    scheduleDateFilter.value = formatDate(nextWeekday());
  }
  renderState(scheduleDayBoard, "Loading doctor day schedule...", "loading-state");
  try {
    const payload = await api(`/api/schedule/day${buildQuery({ date: scheduleDateFilter?.value || "" })}`);
    renderScheduleDay(payload);
  } catch (error) {
    renderState(scheduleDayBoard, error.message, "error-state");
  }
}

async function populateRescheduleDoctors(dateValue, selectedDoctorId = "") {
  if (!rescheduleForm?.doctor_id || !dateValue) return;
  if (currentUserRole === "doctor") {
    const payload = await api("/api/doctors/me");
    const doctor = payload.doctor;
    rescheduleForm.doctor_id.innerHTML = "";
    const option = document.createElement("option");
    option.value = doctor.id;
    option.textContent = `${doctor.name} | ${doctor.department} | ${doctor.shift}`;
    rescheduleForm.doctor_id.appendChild(option);
    rescheduleForm.doctor_id.value = doctor.id;
    return;
  }
  const payload = await api(`/api/doctors${buildQuery({ date: dateValue })}`);
  rescheduleForm.doctor_id.innerHTML = "";
  payload.doctors.forEach((doctor) => {
    const option = document.createElement("option");
    option.value = doctor.id;
    option.textContent = `${doctor.name} | ${doctor.department} | ${doctor.shift}`;
    rescheduleForm.doctor_id.appendChild(option);
  });
  if (selectedDoctorId) rescheduleForm.doctor_id.value = selectedDoctorId;
}

function fillDoctorProfileForm(doctor) {
  if (!doctorProfileForm) return;
  if (doctorProfilePhoto) {
    doctorProfilePhoto.src = assetUrl(doctor.photo);
    doctorProfilePhoto.alt = `${doctor.name} profile photo`;
  }
  Object.entries({
    name: doctor.name,
    department: doctor.department,
    room: doctor.room,
    appointment_focus: doctor.appointment_focus,
    status: doctor.status,
    start_time: doctor.start_time,
    end_time: doctor.end_time,
    slot_minutes: doctor.slot_minutes,
    capacity: doctor.capacity,
    profile: doctor.profile
  }).forEach(([field, value]) => {
    if (doctorProfileForm.elements[field]) {
      doctorProfileForm.elements[field].value = value ?? "";
    }
  });
}

async function loadDoctorProfile() {
  if (!doctorProfileForm) return;
  setMessage(doctorProfileMessage, "Loading doctor profile...");
  try {
    const payload = await api("/api/doctors/me");
    fillDoctorProfileForm(payload.doctor);
    setMessage(doctorProfileMessage, `Profile loaded for ${payload.doctor.name}.`);
  } catch (error) {
    setMessage(doctorProfileMessage, error.message, "error");
  }
}

async function saveDoctorProfile(event) {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(doctorProfileForm).entries());
  setMessage(doctorProfileMessage, "Saving doctor profile...");
  try {
    const payload = await api("/api/doctors/me", {
      method: "PATCH",
      body: JSON.stringify(data)
    });
    fillDoctorProfileForm(payload.doctor);
    setMessage(doctorProfileMessage, "Doctor profile saved. Patient booking and schedule views now use the updated information.");
    await loadAppointments();
    await loadScheduleDay();
  } catch (error) {
    setMessage(doctorProfileMessage, error.message, "error");
  }
}

async function uploadDoctorPhoto(event) {
  event.preventDefault();
  const formData = new FormData(doctorPhotoForm);
  const file = formData.get("photo");
  if (!file || !file.name) {
    setMessage(doctorPhotoMessage, "Choose a PNG, JPG, JPEG, or WEBP photo first.", "error");
    return;
  }
  setMessage(doctorPhotoMessage, "Uploading doctor photo...");
  try {
    const payload = await uploadApi("/api/doctors/me/photo", formData);
    fillDoctorProfileForm(payload.doctor);
    doctorPhotoForm.reset();
    if (doctorPhotoFileName) {
      doctorPhotoFileName.textContent = "No file selected";
    }
    setMessage(doctorPhotoMessage, "Doctor photo uploaded. Patient booking and schedule views now use the new image.");
    await loadScheduleDay();
  } catch (error) {
    setMessage(doctorPhotoMessage, error.message, "error");
  }
}

function updateDoctorPhotoFileName() {
  if (!doctorPhotoInput || !doctorPhotoFileName) {
    return;
  }
  const file = doctorPhotoInput.files && doctorPhotoInput.files[0];
  doctorPhotoFileName.textContent = file ? file.name : "No file selected";
}

function renderAdminDoctorCard(doctor) {
  const card = document.createElement("article");
  card.className = "management-card";
  card.innerHTML = `
    <div>
      <strong>${escapeHtml(doctor.name)}</strong>
      <span>${escapeHtml(doctor.linked_usernames?.join(", ") || "No linked account")}</span>
    </div>
    <div><span>Department</span><strong>${escapeHtml(doctor.department)}</strong></div>
    <div><span>Room</span><strong>${escapeHtml(doctor.room)}</strong></div>
    <div><span>Shift</span><strong>${escapeHtml(doctor.shift)}</strong></div>
    <div><span>Capacity</span><strong>${escapeHtml(doctor.capacity)}</strong></div>
  `;
  return card;
}

async function loadAdminDoctors() {
  if (!adminDoctorList) return;
  renderState(adminDoctorList, "Loading doctor accounts...", "loading-state");
  try {
    const payload = await api("/api/admin/doctors");
    adminDoctorList.innerHTML = "";
    if (!payload.doctors.length) {
      renderState(adminDoctorList, "No doctor profiles are configured.", "empty-state");
      return;
    }
    payload.doctors.forEach((doctor) => adminDoctorList.appendChild(renderAdminDoctorCard(doctor)));
  } catch (error) {
    renderState(adminDoctorList, error.message, "error-state");
  }
}

async function createAdminDoctor(event) {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(adminDoctorForm).entries());
  setMessage(adminDoctorMessage, "Creating doctor account...");
  try {
    const payload = await api("/api/admin/doctors", {
      method: "POST",
      body: JSON.stringify(data)
    });
    adminDoctorForm.reset();
    if (adminDoctorForm.elements.start_time) adminDoctorForm.elements.start_time.value = "09:00";
    if (adminDoctorForm.elements.end_time) adminDoctorForm.elements.end_time.value = "17:00";
    if (adminDoctorForm.elements.slot_minutes) adminDoctorForm.elements.slot_minutes.value = "30";
    if (adminDoctorForm.elements.capacity) adminDoctorForm.elements.capacity.value = "1";
    setMessage(adminDoctorMessage, `${payload.doctor.name} was created and is now visible in patient booking.`);
    await loadAdminDoctors();
    await loadScheduleDay();
  } catch (error) {
    setMessage(adminDoctorMessage, error.message, "error");
  }
}

async function openRescheduleModal() {
  if (!rescheduleModal || !rescheduleForm || !appointmentState.currentDetail) return;
  const appointment = appointmentState.currentDetail;
  rescheduleForm.appointment_id.value = appointment.id;
  rescheduleForm.preferred_date.value = appointment.preferred_date;
  rescheduleForm.preferred_time.value = appointment.preferred_time;
  rescheduleForm.review_note.value = "Appointment rescheduled by clinic staff.";
  setMessage(rescheduleMessage, "");
  await populateRescheduleDoctors(appointment.preferred_date, appointment.doctor_id);
  rescheduleModal.hidden = false;
}

function closeRescheduleModal() {
  if (rescheduleModal) rescheduleModal.hidden = true;
}

async function saveReviewDecision(event) {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(reviewForm).entries());
  setMessage(reviewMessage, "Saving review decision...");
  try {
    await api(`/api/appointments/${data.appointment_id}/review`, {
      method: "PATCH",
      body: JSON.stringify({ status: data.status, review_note: data.review_note })
    });
    setMessage(reviewMessage, "Review decision saved.");
    closeReviewModal();
    await openDetailDrawer(data.appointment_id);
    await loadScheduleDay();
  } catch (error) {
    setMessage(reviewMessage, error.message, "error");
  }
}

async function saveRescheduleDecision(event) {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(rescheduleForm).entries());
  setMessage(rescheduleMessage, "Saving reschedule...");
  try {
    await api(`/api/appointments/${data.appointment_id}/reschedule`, {
      method: "PATCH",
      body: JSON.stringify({
        doctor_id: data.doctor_id,
        preferred_date: data.preferred_date,
        preferred_time: data.preferred_time,
        review_note: data.review_note
      })
    });
    setMessage(rescheduleMessage, "Reschedule saved.");
    closeRescheduleModal();
    await openDetailDrawer(data.appointment_id);
    await loadScheduleDay();
  } catch (error) {
    setMessage(rescheduleMessage, error.message, "error");
  }
}

if (loginForm) {
  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    setMessage(loginMessage, "Signing in...");
    const data = Object.fromEntries(new FormData(loginForm).entries());
    try {
      await performLogin(data.username, data.password);
    } catch (error) {
      setMessage(loginMessage, error.message, "error");
    }
  });

  document.querySelectorAll("[data-demo-login]").forEach((button) => {
    button.addEventListener("click", async () => {
      setMessage(loginMessage, "Signing in...");
      try {
        await performLogin(button.dataset.username, button.dataset.password);
      } catch (error) {
        setMessage(loginMessage, error.message, "error");
      }
    });
  });
}

if (appointmentForm) {
  appointmentForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    setMessage(formMessage, "Submitting appointment request...");
    const data = Object.fromEntries(new FormData(appointmentForm).entries());
    try {
      const payload = await api("/api/appointments", {
        method: "POST",
        body: JSON.stringify(data)
      });
      setMessage(
        formMessage,
        payload.appointment.conflict
          ? "Request submitted. Conflict flagged for staff review."
          : "Request submitted for staff review."
      );
      appointmentForm.reset();
      if (doctorSelect) doctorSelect.innerHTML = '<option value="">Select a date first</option>';
      availabilitySlots.innerHTML = "";
      updateBookingSummary();
      await loadAppointments();
    } catch (error) {
      setMessage(formMessage, error.message, "error");
    }
  });
}

if (dateInput) {
  dateInput.addEventListener("change", async () => {
    timeInput.value = "";
    await loadDoctorRoster(dateInput.value);
    updateBookingSummary();
  });
}

if (registerForm) {
  registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(registerForm).entries());
    if (data.password !== data.confirm_password) {
      setMessage(registerMessage, "Password confirmation does not match.", "error");
      return;
    }
    setMessage(registerMessage, "Creating account...");
    try {
      await performRegistration(data);
    } catch (error) {
      setMessage(registerMessage, error.message, "error");
    }
  });
}

if (doctorSelect) {
  doctorSelect.addEventListener("change", async () => {
    appointmentState.selectedDoctorId = doctorSelect.value;
    timeInput.value = "";
    renderDoctorRoster(appointmentState.doctors);
    await loadAvailability(dateInput.value);
    updateBookingSummary();
  });
}

if (doctorRosterSearch) {
  doctorRosterSearch.addEventListener("input", () => {
    renderDoctorRoster(appointmentState.doctors);
  });
}

if (doctorRosterList) {
  doctorRosterList.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-select-doctor]");
    if (!button || !doctorSelect) return;
    doctorSelect.value = button.dataset.selectDoctor;
    appointmentState.selectedDoctorId = doctorSelect.value;
    doctorRosterList.querySelectorAll(".doctor-card").forEach((card) => {
      card.classList.toggle("is-selected", card.dataset.doctorId === doctorSelect.value);
    });
    timeInput.value = "";
    await loadAvailability(dateInput.value);
    updateBookingSummary();
  });
}

if (availabilitySlots) {
  availabilitySlots.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-slot-time]");
    if (!button || !timeInput) return;
    if (button.classList.contains("is-occupied")) return;
    timeInput.value = button.dataset.slotTime;
    availabilitySlots.querySelectorAll(".slot-button").forEach((slot) => slot.classList.remove("is-selected"));
    button.classList.add("is-selected");
    updateBookingSummary();
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
      } else if (action === "patient-cancel") {
        await cancelPatientAppointment(id);
      } else if (action === "patient-reschedule") {
        await reschedulePatientAppointment(id);
      } else if (action === "open-detail") {
        await openDetailDrawer(id);
      }
    } catch (error) {
      renderState(activeAppointmentList, error.message, "error-state");
    }
  });
}

document.querySelectorAll("[data-close-drawer]").forEach((button) => {
  button.addEventListener("click", closeDetailDrawer);
});

if (scheduleDayBoard) {
  scheduleDayBoard.addEventListener("click", async (event) => {
    const button = event.target.closest("button[data-action='open-detail']");
    if (!button) return;
    await openDetailDrawer(button.dataset.id);
  });
}

document.querySelectorAll("[data-review-status]").forEach((button) => {
  button.addEventListener("click", () => openReviewModal(button.dataset.reviewStatus));
});

document.querySelectorAll("[data-close-review]").forEach((button) => {
  button.addEventListener("click", closeReviewModal);
});

document.querySelectorAll("[data-open-reschedule]").forEach((button) => {
  button.addEventListener("click", openRescheduleModal);
});

document.querySelectorAll("[data-close-reschedule]").forEach((button) => {
  button.addEventListener("click", closeRescheduleModal);
});

if (reviewForm) {
  reviewForm.addEventListener("submit", saveReviewDecision);
}

if (rescheduleForm) {
  rescheduleForm.addEventListener("submit", saveRescheduleDecision);
  rescheduleForm.preferred_date.addEventListener("change", () => {
    populateRescheduleDoctors(rescheduleForm.preferred_date.value, rescheduleForm.doctor_id.value)
      .catch((error) => setMessage(rescheduleMessage, error.message, "error"));
  });
}

if (doctorProfileForm) {
  doctorProfileForm.addEventListener("submit", saveDoctorProfile);
}

if (doctorPhotoForm) {
  doctorPhotoForm.addEventListener("submit", uploadDoctorPhoto);
}

if (doctorPhotoChoose && doctorPhotoInput) {
  doctorPhotoChoose.addEventListener("click", () => doctorPhotoInput.click());
}

if (doctorPhotoInput) {
  doctorPhotoInput.addEventListener("change", updateDoctorPhotoFileName);
}

if (adminDoctorForm) {
  adminDoctorForm.addEventListener("submit", createAdminDoctor);
}

function resetAndLoadStaff() {
  appointmentState.staffPage = 1;
  loadAppointments();
}

function resetAndLoadPatient() {
  appointmentState.patientPage = 1;
  loadAppointments();
}

async function refreshWorkspace() {
  await loadAppointments();
  if (pageName === "staff") {
    await loadScheduleDay();
    await loadAdminDoctors();
    await loadDoctorProfile();
  }
}

if (refreshButton) refreshButton.addEventListener("click", refreshWorkspace);
if (scheduleRefreshButton) scheduleRefreshButton.addEventListener("click", loadScheduleDay);
if (scheduleDateFilter) scheduleDateFilter.addEventListener("change", loadScheduleDay);
if (statusFilter) statusFilter.addEventListener("change", resetAndLoadStaff);
if (staffDateFilter) staffDateFilter.addEventListener("input", resetAndLoadStaff);
if (staffSearch) staffSearch.addEventListener("input", resetAndLoadStaff);
if (patientStatusFilter) patientStatusFilter.addEventListener("change", resetAndLoadPatient);
if (patientSearch) patientSearch.addEventListener("input", resetAndLoadPatient);

if (patientPrevPage) {
  patientPrevPage.addEventListener("click", () => {
    appointmentState.patientPage = Math.max(appointmentState.patientPage - 1, 1);
    loadAppointments();
  });
}

if (patientNextPage) {
  patientNextPage.addEventListener("click", () => {
    appointmentState.patientPage += 1;
    loadAppointments();
  });
}

if (staffPrevPage) {
  staffPrevPage.addEventListener("click", () => {
    appointmentState.staffPage = Math.max(appointmentState.staffPage - 1, 1);
    loadAppointments();
  });
}

if (staffNextPage) {
  staffNextPage.addEventListener("click", () => {
    appointmentState.staffPage += 1;
    loadAppointments();
  });
}

if (pageName === "patient" || pageName === "staff") {
  loadAppointments();
}

if (pageName === "patient") {
  loadDoctorRoster();
}

if (pageName === "staff") {
  loadDoctorProfile();
  loadAdminDoctors();
  loadScheduleDay();
}
