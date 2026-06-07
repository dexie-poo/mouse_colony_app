const API_BASE =
  window.location.protocol === "file:" ? "http://127.0.0.1:8000" : window.location.origin;

const authPanel = document.querySelector("#authPanel");
const appContent = document.querySelector("#appContent");
const loginForm = document.querySelector("#loginForm");
const registerForm = document.querySelector("#registerForm");
const importForm = document.querySelector("#importForm");
const mouseForm = document.querySelector("#mouseForm");
const assignForm = document.querySelector("#assignForm");
const assignMouseSearchInput = document.querySelector("#assignMouseSearchInput");
const matingForm = document.querySelector("#matingForm");
const addPupButton = document.querySelector("#addPupButton");
const pupRows = document.querySelector("#pupRows");
const analysisForm = document.querySelector("#analysisForm");
const analysisMouseSelect = document.querySelector("#analysisMouseSelect");
const analysisRecordMouseSelect = document.querySelector("#analysisRecordMouseSelect");
const analysisSearchInput = document.querySelector("#analysisSearchInput");
const clearAnalysisSearchButton = document.querySelector("#clearAnalysisSearchButton");
const analysisList = document.querySelector("#analysisList");
const currentUserLabel = document.querySelector("#currentUserLabel");
const logoutButton = document.querySelector("#logoutButton");
const exportButton = document.querySelector("#exportButton");
const exportLitterHistoryButton = document.querySelector("#exportLitterHistoryButton");
const refreshButton = document.querySelector("#refreshButton");
const mouseTableBody = document.querySelector("#mouseTableBody");
const assignMouseSelect = document.querySelector("#assignMouseSelect");
const sireSelect = document.querySelector("#sireSelect");
const damSelect = document.querySelector("#damSelect");
const historyMouseSelect = document.querySelector("#historyMouseSelect");
const matingHistorySearchInput = document.querySelector("#matingHistorySearchInput");
const clearMatingHistorySearchButton = document.querySelector("#clearMatingHistorySearchButton");
const cageNumbers = document.querySelector("#cageNumbers");
const matingHistory = document.querySelector("#matingHistory");
const statusBox = document.querySelector("#status");
const tabButtons = document.querySelectorAll("[data-tab]");
const tabPanels = document.querySelectorAll("[data-tab-panel]");

let mice = [];
let cages = [];
let matings = [];
let analyses = [];
let displayedAnalyses = [];
let authToken = localStorage.getItem("mouse_colony_token");
let currentUser = JSON.parse(localStorage.getItem("mouse_colony_user") || "null");

function showStatus(message, timeout = 3500) {
  statusBox.textContent = message;
  window.clearTimeout(showStatus.timeout);
  if (timeout !== null) {
    showStatus.timeout = window.setTimeout(() => {
      statusBox.textContent = "";
    }, timeout);
  }
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
      ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
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

function setAuth(token, user) {
  authToken = token;
  currentUser = user;
  localStorage.setItem("mouse_colony_token", token);
  localStorage.setItem("mouse_colony_user", JSON.stringify(user));
  renderAuthState();
}

function clearAuth() {
  authToken = null;
  currentUser = null;
  localStorage.removeItem("mouse_colony_token");
  localStorage.removeItem("mouse_colony_user");
  renderAuthState();
}

function showTab(tabName) {
  tabButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.tab === tabName);
  });
  tabPanels.forEach((panel) => {
    panel.classList.toggle("hidden", panel.dataset.tabPanel !== tabName);
  });
}

function renderAuthState() {
  const loggedIn = Boolean(authToken);
  authPanel.classList.toggle("hidden", loggedIn);
  appContent.classList.toggle("hidden", !loggedIn);
  exportButton.classList.toggle("hidden", !loggedIn);
  refreshButton.classList.toggle("hidden", !loggedIn);
  logoutButton.classList.toggle("hidden", !loggedIn);
  currentUserLabel.textContent = currentUser ? currentUser.username : "";
}

async function fileToDataUrl(file) {
  if (!file) {
    return null;
  }

  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

function mouseLabel(mouse) {
  return `#${mouse.external_id || mouse.id} ${mouse.genotype} ${mouse.gender}`;
}

function cageNumber(mouse) {
  return mouse.cage ? mouse.cage.cage_number : "";
}

function searchableMouseText(mouse) {
  return [mouse.id, mouse.external_id, mouse.genotype, mouse.gender, mouse.owner, cageNumber(mouse)]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
}

function renderMouseSelect(select, placeholder = "Select mouse", filterText = "") {
  const currentValue = select.value;
  const query = filterText.trim().toLowerCase();
  const options = query
    ? mice.filter((mouse) => searchableMouseText(mouse).includes(query))
    : mice;

  select.innerHTML = [
    `<option value="">${placeholder}</option>`,
    ...options.map((mouse) => `<option value="${mouse.id}">${mouseLabel(mouse)}</option>`),
  ].join("");

  if (options.some((mouse) => String(mouse.id) === currentValue)) {
    select.value = currentValue;
  } else if (query && options.length === 1) {
    select.value = String(options[0].id);
  }
}

function renderControls() {
  renderMouseSelect(assignMouseSelect, "Select mouse", assignMouseSearchInput.value);
  renderMouseSelect(sireSelect, "Select sire");
  renderMouseSelect(damSelect, "Select dam");
  renderMouseSelect(historyMouseSelect);
  renderMouseSelect(analysisMouseSelect);

  const analysedMouseIds = new Set(analyses.map((analysis) => analysis.mouse_id));
  analysisRecordMouseSelect.innerHTML = [
    `<option value="">All analysed mice</option>`,
    ...mice
      .filter((mouse) => analysedMouseIds.has(mouse.id))
      .map((mouse) => `<option value="${mouse.id}">${mouseLabel(mouse)}</option>`),
  ].join("");

  cageNumbers.innerHTML = cages
    .map((cage) => `<option value="${cage.cage_number}"></option>`)
    .join("");
}

function renderMouseTable() {
  mouseTableBody.innerHTML = mice
    .map((mouse) => {
      return `
        <tr>
          <td>${mouse.external_id || mouse.id}</td>
          <td>${mouse.gender}</td>
          <td>${mouse.dob || ""}</td>
          <td>${mouse.age_months || ""}</td>
          <td>${mouse.genotype}</td>
          <td>${mouse.owner || ""}</td>
          <td>${mouse.remark || ""}</td>
          <td>${cageNumber(mouse) || "Unassigned"}</td>
          <td>${mouse.sacrificed || ""}</td>
          <td><button type="button" class="link-button" data-history-id="${mouse.id}">History</button></td>
        </tr>
      `;
    })
    .join("");
}

function matingSearchText(mating) {
  const sire = mice.find((mouse) => mouse.id === mating.sire_id);
  const dam = mice.find((mouse) => mouse.id === mating.dam_id);
  return [
    mating.mating_date,
    mating.litter_dob,
    mating.litter_size,
    mating.male_pups,
    mating.female_pups,
    mating.pup_genotypes,
    mating.kept_mouse_ids,
    mating.notes,
    sire ? mouseLabel(sire) : mating.sire_id,
    dam ? mouseLabel(dam) : mating.dam_id,
  ]
    .filter((value) => value !== null && value !== undefined && value !== "")
    .join(" ")
    .toLowerCase();
}

function renderMatingHistory() {
  const mouseId = historyMouseSelect.value;
  const query = matingHistorySearchInput.value.trim().toLowerCase();

  if (!mouseId && !query) {
    matingHistory.innerHTML = `<p class="empty-state">Select a mouse or search mating history.</p>`;
    return;
  }

  const selectedId = mouseId ? Number(mouseId) : null;
  const records = matings.filter((mating) => {
    const matchesMouse =
      selectedId === null || mating.sire_id === selectedId || mating.dam_id === selectedId;
    const matchesSearch = !query || matingSearchText(mating).includes(query);
    return matchesMouse && matchesSearch;
  });

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
          <span>Created mouse IDs: ${mating.kept_mouse_ids || ""}</span>
          <span>${mating.notes || ""}</span>
        </article>
      `;
    })
    .join("");
}

function renderAnalyses(records = displayedAnalyses) {
  if (!records.length) {
    analysisList.innerHTML = `<p class="empty-state">No analysis records.</p>`;
    return;
  }

  analysisList.innerHTML = records
    .map((analysis) => {
      const mouse = mice.find((item) => item.id === analysis.mouse_id);
      const image = analysis.image_data
        ? `<img class="analysis-image" src="${analysis.image_data}" alt="${analysis.image_filename || "analysis image"}" />`
        : "";
      return `
        <article class="history-item">
          <strong>${mouse ? mouseLabel(mouse) : `Mouse #${analysis.mouse_id}`} sacrificed ${analysis.sacrifice_date || ""}</strong>
          <span>Age at sacrifice: ${analysis.age_at_sacrifice || ""}</span>
          <span>Organs: ${analysis.organs_extracted || ""}</span>
          <span>Conditions: ${analysis.organ_conditions || ""}</span>
          <span>Preservation: ${analysis.preservation_method || ""}</span>
          <span>${analysis.notes || ""}</span>
          ${image}
        </article>
      `;
    })
    .join("");
}

async function loadAnalyses(path = "/analyses/") {
  displayedAnalyses = await request(path);
  analyses = path === "/analyses/" ? displayedAnalyses : analyses;
  renderControls();
  renderAnalyses(displayedAnalyses);
}

function addPupRow(defaults = {}) {
  const row = document.createElement("div");
  row.className = "pup-row";
  row.innerHTML = `
    <input name="pup_label" placeholder="M1 / F3" value="${defaults.pup_label || ""}" />
    <select name="sex">
      <option value="Male" ${defaults.sex === "Male" ? "selected" : ""}>Male</option>
      <option value="Female" ${defaults.sex === "Female" ? "selected" : ""}>Female</option>
    </select>
    <input name="genotype" placeholder="Genotype" value="${defaults.genotype || ""}" />
    <input name="genotype_reference_1" placeholder="Genotype Ref #1" value="${defaults.genotype_reference_1 || ""}" />
    <input name="genotype_reference_2" placeholder="Genotype Ref #2" value="${defaults.genotype_reference_2 || ""}" />
    <select name="decision">
      <option value="euthanise" ${defaults.decision !== "keep" ? "selected" : ""}>Euthanise</option>
      <option value="keep" ${defaults.decision === "keep" ? "selected" : ""}>Keep</option>
    </select>
    <input name="assigned_external_id" placeholder="Assigned ID# if kept" value="${defaults.assigned_external_id || ""}" />
    <input name="wean_date" type="date" value="${defaults.wean_date || ""}" />
    <button type="button" class="link-button" data-remove-pup>Remove</button>
  `;
  pupRows.appendChild(row);
}

function collectPups() {
  return [...pupRows.querySelectorAll(".pup-row")]
    .map((row) => {
      const fields = Object.fromEntries(
        [...row.querySelectorAll("input, select")].map((input) => [input.name, input.value]),
      );
      return {
        pup_label: nullable(fields.pup_label),
        assigned_external_id: nullable(fields.assigned_external_id),
        sex: fields.sex,
        wean_date: nullable(fields.wean_date),
        genotype: nullable(fields.genotype),
        genotype_reference_1: nullable(fields.genotype_reference_1),
        genotype_reference_2: nullable(fields.genotype_reference_2),
        decision: fields.decision,
      };
    })
    .filter((pup) => pup.pup_label || pup.assigned_external_id || pup.genotype);
}

async function loadData() {
  [mice, cages, matings, analyses] = await Promise.all([
    request("/mice/"),
    request("/cages/"),
    request("/matings/"),
    request("/analyses/"),
  ]);
  displayedAnalyses = analyses;

  renderControls();
  renderMouseTable();
  renderMatingHistory();
  renderAnalyses(displayedAnalyses);
}

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = formPayload(loginForm);
  const result = await request("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  setAuth(result.token, result.user);
  loginForm.reset();
  showStatus("Logged in");
  await loadData();
});

registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = formPayload(registerForm);
  await request("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  registerForm.reset();
  showStatus("User created");
});

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

importForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const file = importForm.elements.file.files[0];
  const submitButton = importForm.querySelector('button[type="submit"]');
  if (!file) {
    showStatus("Please choose an Excel file first.");
    return;
  }

  const data = new FormData();
  data.append("file", file);

  submitButton.disabled = true;
  submitButton.textContent = "Importing...";
  showStatus(`Importing ${file.name}...`, null);

  try {
    const response = await fetch(`${API_BASE}/mice/import.xlsx`, {
      method: "POST",
      headers: { Authorization: `Bearer ${authToken}` },
      body: data,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Import failed with status ${response.status}`);
    }

    const result = await response.json();
    importForm.reset();
    showStatus(`Imported ${result.imported} mice. Matched: ${result.matched_fields.join(", ")}`, 8000);
    await loadData();
  } catch (error) {
    showStatus(`Import failed: ${error.message}`, 10000);
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "Import Mice";
  }
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
  payload.pups = collectPups();
  payload.notes = nullable(payload.notes);

  await request("/matings/", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  matingForm.reset();
  pupRows.innerHTML = "";
  showStatus("Mating recorded");
  await loadData();
});

addPupButton.addEventListener("click", () => {
  addPupRow();
});

pupRows.addEventListener("click", (event) => {
  if (event.target.closest("[data-remove-pup]")) {
    event.target.closest(".pup-row").remove();
  }
});

analysisForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = formPayload(analysisForm);
  const imageFile = analysisForm.elements.image.files[0];
  payload.mouse_id = Number(payload.mouse_id);
  payload.sacrifice_date = nullable(payload.sacrifice_date);
  payload.age_at_sacrifice = nullable(payload.age_at_sacrifice);
  payload.organs_extracted = nullable(payload.organs_extracted);
  payload.organ_conditions = nullable(payload.organ_conditions);
  payload.preservation_method = nullable(payload.preservation_method);
  payload.image_filename = imageFile ? imageFile.name : null;
  payload.image_data = await fileToDataUrl(imageFile);
  payload.notes = nullable(payload.notes);
  delete payload.image;

  await request("/analyses/", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  analysisForm.reset();
  showStatus("Analysis recorded");
  await loadData();
});

analysisSearchInput.addEventListener("input", async () => {
  const query = analysisSearchInput.value.trim();
  analysisRecordMouseSelect.value = "";
  if (!query) {
    await loadAnalyses();
    return;
  }
  await loadAnalyses(`/analyses/?q=${encodeURIComponent(query)}`);
});

analysisRecordMouseSelect.addEventListener("change", async () => {
  analysisSearchInput.value = "";
  const mouseId = analysisRecordMouseSelect.value;
  if (!mouseId) {
    await loadAnalyses();
    return;
  }
  await loadAnalyses(`/analyses/mouse/${mouseId}`);
});

clearAnalysisSearchButton.addEventListener("click", async () => {
  analysisSearchInput.value = "";
  analysisRecordMouseSelect.value = "";
  await loadAnalyses();
});

historyMouseSelect.addEventListener("change", () => {
  renderMatingHistory();
});

matingHistorySearchInput.addEventListener("input", () => {
  renderMatingHistory();
});

clearMatingHistorySearchButton.addEventListener("click", () => {
  historyMouseSelect.value = "";
  matingHistorySearchInput.value = "";
  renderMatingHistory();
});

assignMouseSearchInput.addEventListener("input", () => {
  renderMouseSelect(assignMouseSelect, "Select mouse", assignMouseSearchInput.value);
});

tabButtons.forEach((button) => {
  button.addEventListener("click", () => {
    showTab(button.dataset.tab);
  });
});

mouseTableBody.addEventListener("click", (event) => {
  const historyButton = event.target.closest("[data-history-id]");
  if (!historyButton) {
    return;
  }

  historyMouseSelect.value = historyButton.dataset.historyId;
  showTab("mating");
  renderMatingHistory();
});

refreshButton.addEventListener("click", () => {
  loadData().then(() => showStatus("Data refreshed"));
});

exportButton.addEventListener("click", async () => {
  const response = await fetch(`${API_BASE}/mice/export.xlsx`, {
    headers: { Authorization: `Bearer ${authToken}` },
  });
  if (!response.ok) {
    throw new Error("Export failed");
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "mice_cage_list.xlsx";
  link.click();
  URL.revokeObjectURL(url);
});

exportLitterHistoryButton.addEventListener("click", async () => {
  const response = await fetch(`${API_BASE}/matings/litter-history/export.xlsx`, {
    headers: { Authorization: `Bearer ${authToken}` },
  });
  if (!response.ok) {
    throw new Error("Litter history export failed");
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "litter_history.xlsx";
  link.click();
  URL.revokeObjectURL(url);
});

logoutButton.addEventListener("click", () => {
  clearAuth();
  mice = [];
  cages = [];
  matings = [];
  analyses = [];
  displayedAnalyses = [];
});

renderAuthState();

if (authToken) {
  loadData().catch((error) => {
    clearAuth();
    showStatus(error.message);
  });
}

window.addEventListener("error", (event) => {
  showStatus(event.message);
});

window.addEventListener("unhandledrejection", (event) => {
  const message = event.reason instanceof Error ? event.reason.message : String(event.reason);
  showStatus(message);
});
