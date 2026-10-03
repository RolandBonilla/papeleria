/* Utilidades compartidas por todas las páginas. */
const NAV_LINKS = [
  ["index.html", "Resumen"], ["products.html", "Productos"], ["inventory.html", "Inventario"],
  ["sales.html", "Ventas"], ["clients.html", "Clientes"], ["reports.html", "Reportes"],
];

function getSession() {
  try { return JSON.parse(localStorage.getItem("session") || "null"); } catch { return null; }
}

function logout() {
  localStorage.removeItem("session");
  location.href = "login.html";
}

function requireLogin() {
  const session = getSession();
  if (!session) { location.href = "login.html"; return null; }
  const current = location.pathname.split("/").pop() || "index.html";
  document.getElementById("nav").innerHTML = NAV_LINKS.map(([href, label]) =>
    `<a href="${href}" ${href === current ? 'class="active" aria-current="page"' : ""}>${label}</a>`).join("");
  document.getElementById("user-box").innerHTML =
    `<div>${esc(session.full_name)}<br><small>${esc(session.role)}</small></div><button type="button" id="logout-btn">Cerrar sesión</button>`;
  document.getElementById("logout-btn").addEventListener("click", logout);
  return session;
}

function hasRole(session, ...roles) { return roles.includes(session.role); }

function errorText(data) {
  if (!data || !data.detail) return "Ocurrió un error inesperado";
  if (typeof data.detail === "string") return data.detail;
  return data.detail.map(e => `${(e.loc || []).slice(1).join(".")}: ${e.msg}`).join("; ");
}

async function api(path, { method = "GET", body } = {}) {
  const session = getSession();
  const headers = { "Content-Type": "application/json" };
  if (session) headers.Authorization = `Bearer ${session.access_token}`;
  const response = await fetch(`/api${path}`, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
  if (response.status === 401 && path !== "/auth/login") { logout(); throw new Error("Sesión expirada"); }
  if (response.status === 204) return null;
  const data = await response.json().catch(() => null);
  if (!response.ok) throw new Error(errorText(data));
  return data;
}

function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function money(value) { return "$" + Number(value).toFixed(2); }

function formatDate(iso) { return new Date(iso).toLocaleString("es-EC"); }

function showMessage(text, type = "ok") {
  const box = document.getElementById("message");
  box.textContent = text;
  box.className = `message ${type}`;
}

function clearMessage() { document.getElementById("message").className = "message"; }

function statusBadge(status) {
  const css = status === "Disponible" ? "disponible" : status === "Stock bajo" ? "bajo" : "sin";
  return `<span class="badge ${css}">${esc(status)}</span>`;
}

function fillSelect(select, items, label, placeholder) {
  const first = placeholder === undefined ? "" : `<option value="">${esc(placeholder)}</option>`;
  select.innerHTML = first + items.map(i => `<option value="${i.id}">${esc(label(i))}</option>`).join("");
}

async function guarded(action) {
  try { clearMessage(); await action(); } catch (error) { showMessage(error.message, "error"); }
}
