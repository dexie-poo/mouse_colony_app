const API_BASE =
  window.location.protocol === "file:" ? "http://127.0.0.1:8000" : window.location.origin;

const authPanel = document.querySelector("#authPanel");
const appContent = document.querySelector("#appContent");
const loginForm = document.querySelector("#loginForm");
const registerForm = document.querySelector("#registerForm");
const mouseForm = document.querySelector("#mouseForm");
const assignForm = document.querySelector("#assignForm");
const matingForm = document.querySelector("#matingForm");
const analysisForm = document.querySelector("#analysisForm");
const analysisMouseSelect = document.querySelector("#analysisMouseSelect");
const analysisList = document.querySelector("#analysisList");
const currentUserLabel = document.querySelector("#currentUserLabel");
const logoutButton = document.querySelector("#logoutButton");
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
let analyses = [];
let authToken = localStorage.getItem("mouse_colony_token");
let currentUser = JSON.parse(localStorage.getItem("mouse_colony_user") || "null");

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
  renderMouseSelect(analysisMouseSelect);

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
          <td>${mouse.sacrificed || ""}</td>
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
          <span>Genotyping reference: ${mating.genotyping_reference || ""}</span>
          <span>Decision: ${mating.keep_litter ? "Keep" : ""} ${mating.euthanise_litter ? "Euthanise" : ""}</span>
          <span>Created mouse IDs: ${mating.kept_mouse_ids || ""}</span>
          <span>${mating.notes || ""}</span>
        </article>
      `;
    })
    .join("");
}

function renderAnalyses() {
  if (!analyses.length) {
    analysisList.innerHTML = `<p class="empty-state">No analysis records.</p>`;
    return;
  }

  analysisList.innerHTML = analyses
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

async function loadData() {
  [mice, cages, matings, analyses] = await Promise.all([
    request("/mice/"),
    request("/cages/"),
    request("/matings/"),
    request("/analyses/"),
  ]);

  renderControls();
  renderMouseTable();
  renderMatingHistory(historyMouseSelect.value);
  renderAnalyses();
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
  payload.genotyping_reference = nullable(payload.genotyping_reference);
  payload.keep_litter = Boolean(payload.keep_litter);
  payload.euthanise_litter = Boolean(payload.euthanise_litter);
  payload.kept_male_pups = optionalNumber(payload.kept_male_pups);
  payload.kept_female_pups = optionalNumber(payload.kept_female_pups);
  payload.kept_pup_genotype = nullable(payload.kept_pup_genotype);
  payload.notes = nullable(payload.notes);

  await request("/matings/", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  matingForm.reset();
  showStatus("Mating recorded");
  await loadData();
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

logoutButton.addEventListener("click", () => {
  clearAuth();
  mice = [];
  cages = [];
  matings = [];
  analyses = [];
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
