const API_BASE =
  window.location.protocol === "file:" ? "http://127.0.0.1:8000" : window.location.origin;

const mouseForm = document.querySelector("#mouseForm");
const assignForm = document.querySelector("#assignForm");
const matingForm = document.querySelector("#matingForm");
const exportButton = document.querySelector("#exportButton");
const refreshButton = document.querySelector("#refreshButton");
const mouseTableBody = document.querySelector("#mouseTableBody");
const assignMouseSelect = document.querySelector("#assignMouseSelect");
const sireSelect = document.querySelector("#sireSelect");
const damSelect = document.querySelector("#damSelect");
const historyMouseSelect = document.querySelector("#historyMouseSelect");
const cageNumbers = document.querySelector("#cageNumbers");
const matingHistory = document.querySelector("#matingHistory");
const statusBox = document.querySelector("#status");

let mice = [];
let cages = [];
let matings = [];

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

function optionalNumber(value) {
  return value === "" ? null : Number(value);
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
    const detail = Array.isArray(error.detail)
      ? error.detail.map((item) => item.msg).join(", ")
      : error.detail;
    throw new Error(detail || `Request failed: ${response.status}`);
  }

  return response.json();
}

function mouseLabel(mouse) {
  return `#${mouse.id} ${mouse.genotype} ${mouse.gender}`;
}

function cageNumber(mouse) {
  return mouse.cage ? mouse.cage.cage_number : "";
}

function renderMouseSelect(select, placeholder = "Select mouse") {
  select.innerHTML = [
    `<option value="">${placeholder}</option>`,
    ...mice.map((mouse) => `<option value="${mouse.id}">${mouseLabel(mouse)}</option>`),
  ].join("");
}

function renderControls() {
  renderMouseSelect(assignMouseSelect);
  renderMouseSelect(sireSelect, "Select sire");
  renderMouseSelect(damSelect, "Select dam");
  renderMouseSelect(historyMouseSelect);

  cageNumbers.innerHTML = cages
    .map((cage) => `<option value="${cage.cage_number}"></option>`)
    .join("");
}

function renderMouseTable() {
  mouseTableBody.innerHTML = mice
    .map((mouse) => {
      return `
        <tr>
          <td>${mouse.id}</td>
          <td>${mouse.gender}</td>
          <td>${mouse.dob || ""}</td>
          <td>${mouse.age_months || ""}</td>
          <td>${mouse.genotype}</td>
          <td>${mouse.owner || ""}</td>
          <td>${mouse.remark || ""}</td>
          <td>${cageNumber(mouse) || "Unassigned"}</td>
          <td><button type="button" class="link-button" data-history-id="${mouse.id}">History</button></td>
        </tr>
      `;
    })
    .join("");
}

function renderMatingHistory(mouseId) {
  if (!mouseId) {
    matingHistory.innerHTML = "";
    return;
  }

  const selectedId = Number(mouseId);
  const records = matings.filter(
    (mating) => mating.sire_id === selectedId || mating.dam_id === selectedId,
  );

  if (!records.length) {
    matingHistory.innerHTML = `<p class="empty-state">No mating history recorded.</p>`;
    return;
  }

  matingHistory.innerHTML = records
    .map((mating, index) => {
      const sire = mice.find((mouse) => mouse.id === mating.sire_id);
      const dam = mice.find((mouse) => mouse.id === mating.dam_id);
      const date = mating.litter_dob || mating.mating_date || "Date not recorded";
      return `
        <article class="history-item">
          <strong>${index + 1}. ${date} -> ${mating.male_pups ?? 0} male ${mating.female_pups ?? 0} female</strong>
          <span>Sire ${sire ? mouseLabel(sire) : mating.sire_id} x Dam ${dam ? mouseLabel(dam) : mating.dam_id}</span>
          <span>Litter size: ${mating.litter_size ?? ""}</span>
          <span>Pup genotypes: ${mating.pup_genotypes || ""}</span>
          <span>${mating.notes || ""}</span>
        </article>
      `;
    })
    .join("");
}

async function loadData() {
  [mice, cages, matings] = await Promise.all([
    request("/mice/"),
    request("/cages/"),
    request("/matings/"),
  ]);

  renderControls();
  renderMouseTable();
  renderMatingHistory(historyMouseSelect.value);
}

mouseForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = formPayload(mouseForm);
  payload.dob = nullable(payload.dob);
  payload.owner = nullable(payload.owner);
  payload.remark = nullable(payload.remark);
  payload.cage_number = nullable(payload.cage_number);

  await request("/mice/", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  mouseForm.reset();
  showStatus("Mouse added");
  await loadData();
});

assignForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = formPayload(assignForm);
  await request(`/mice/${payload.mouse_id}/assign-cage/${encodeURIComponent(payload.cage_number)}`, {
    method: "POST",
  });

  assignForm.reset();
  showStatus("Mouse transferred to cage");
  await loadData();
});

matingForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = formPayload(matingForm);
  payload.sire_id = Number(payload.sire_id);
  payload.dam_id = Number(payload.dam_id);
  payload.mating_date = nullable(payload.mating_date);
  payload.litter_dob = nullable(payload.litter_dob);
  payload.litter_size = optionalNumber(payload.litter_size);
  payload.male_pups = optionalNumber(payload.male_pups);
  payload.female_pups = optionalNumber(payload.female_pups);
  payload.pup_genotypes = nullable(payload.pup_genotypes);
  payload.notes = nullable(payload.notes);

  await request("/matings/", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  matingForm.reset();
  showStatus("Mating recorded");
  await loadData();
});

historyMouseSelect.addEventListener("change", () => {
  renderMatingHistory(historyMouseSelect.value);
});

mouseTableBody.addEventListener("click", (event) => {
  const historyButton = event.target.closest("[data-history-id]");
  if (!historyButton) {
    return;
  }

  historyMouseSelect.value = historyButton.dataset.historyId;
  renderMatingHistory(historyMouseSelect.value);
});

refreshButton.addEventListener("click", () => {
  loadData().then(() => showStatus("Data refreshed"));
});

exportButton.addEventListener("click", () => {
  window.location.href = `${API_BASE}/mice/export.xlsx`;
});

loadData().catch((error) => {
  showStatus(error.message);
});
