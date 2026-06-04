const API_BASE = "http://127.0.0.1:8000";

const mouseForm = document.querySelector("#mouseForm");
const cageForm = document.querySelector("#cageForm");
const assignForm = document.querySelector("#assignForm");
const refreshButton = document.querySelector("#refreshButton");
const mouseTableBody = document.querySelector("#mouseTableBody");
const mouseCageSelect = document.querySelector("#mouseCageSelect");
const assignMouseSelect = document.querySelector("#assignMouseSelect");
const assignCageSelect = document.querySelector("#assignCageSelect");
const statusBox = document.querySelector("#status");

let mice = [];
let cages = [];

function showStatus(message) {
  statusBox.textContent = message;
  window.clearTimeout(showStatus.timeout);
  showStatus.timeout = window.setTimeout(() => {
    statusBox.textContent = "";
  }, 3500);
}

function nullable(value) {
  return value === "" ? null : value;
}

function formPayload(form) {
  const data = new FormData(form);
  return Object.fromEntries(data.entries());
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `Request failed: ${response.status}`);
  }

  return response.json();
}

function renderCageOptions() {
  const cageOptions = cages
    .map((cage) => `<option value="${cage.id}">${cage.name}</option>`)
    .join("");

  mouseCageSelect.innerHTML = `<option value="">Unassigned</option>${cageOptions}`;
  assignCageSelect.innerHTML = `<option value="">Select cage</option>${cageOptions}`;
}

function renderMouseOptions() {
  assignMouseSelect.innerHTML = mice
    .map((mouse) => {
      const label = `#${mouse.id} ${mouse.genotype} ${mouse.gender}`;
      return `<option value="${mouse.id}">${label}</option>`;
    })
    .join("");
}

function renderMouseTable() {
  mouseTableBody.innerHTML = mice
    .map((mouse) => {
      const cageName = mouse.cage ? mouse.cage.name : "Unassigned";
      return `
        <tr>
          <td>${mouse.id}</td>
          <td>${mouse.genotype}</td>
          <td>${mouse.gender}</td>
          <td>${mouse.project || ""}</td>
          <td>${mouse.dob || ""}</td>
          <td>${mouse.age || ""}</td>
          <td>${mouse.age_analysed || ""}</td>
          <td>${cageName}</td>
          <td>${mouse.notes || ""}</td>
        </tr>
      `;
    })
    .join("");
}

async function loadData() {
  [mice, cages] = await Promise.all([request("/mice/"), request("/cages/")]);

  renderCageOptions();
  renderMouseOptions();
  renderMouseTable();
}

mouseForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = formPayload(mouseForm);
  payload.project = nullable(payload.project);
  payload.dob = nullable(payload.dob);
  payload.age = nullable(payload.age);
  payload.age_analysed = nullable(payload.age_analysed);
  payload.notes = nullable(payload.notes);
  payload.cage_id = payload.cage_id ? Number(payload.cage_id) : null;

  await request("/mice/", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  mouseForm.reset();
  showStatus("Mouse added");
  await loadData();
});

cageForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = formPayload(cageForm);
  payload.location = nullable(payload.location);
  payload.notes = nullable(payload.notes);

  await request("/cages/", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  cageForm.reset();
  showStatus("Cage added");
  await loadData();
});

assignForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = formPayload(assignForm);
  await request(`/mice/${payload.mouse_id}/assign-cage/${payload.cage_id}`, {
    method: "POST",
  });

  showStatus("Mouse assigned to cage");
  await loadData();
});

refreshButton.addEventListener("click", () => {
  loadData().then(() => showStatus("Data refreshed"));
});

loadData().catch((error) => {
  showStatus(error.message);
});
