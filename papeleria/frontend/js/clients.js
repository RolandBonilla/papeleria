let session;
const field = id => document.getElementById(id);

function resetForm() {
  field("client-form").reset();
  field("client-id").value = "";
  field("form-title").textContent = "Registrar cliente";
  field("cancel-btn").hidden = true;
}

async function loadClients() {
  const q = field("search-q").value.trim();
  const clients = await api(`/clients${q ? `?q=${encodeURIComponent(q)}` : ""}`);
  const canEdit = hasRole(session, "ADMINISTRADOR", "VENDEDOR");
  field("clients-body").innerHTML = clients.length ? clients.map(c => `
    <tr><td>${esc(c.cedula)}</td><td>${esc(c.name)}</td><td>${esc(c.phone || "")}</td><td>${esc(c.email || "")}</td>
    <td>${canEdit ? `<button class="secondary small" data-edit="${c.id}">Editar</button>` : ""}</td></tr>`).join("")
    : '<tr><td colspan="5" class="empty">No se encontraron clientes.</td></tr>';
  window.currentClients = clients;
}

async function init() {
  session = requireLogin();
  if (!session) return;
  field("form-panel").hidden = !hasRole(session, "ADMINISTRADOR", "VENDEDOR");
  await guarded(loadClients);
  field("client-form").addEventListener("submit", e => {
    e.preventDefault();
    guarded(async () => {
      const id = field("client-id").value;
      const body = {
        cedula: field("cedula").value.trim(), name: field("name").value,
        phone: field("phone").value.trim() || null, email: field("email").value.trim() || null,
      };
      await api(id ? `/clients/${id}` : "/clients", { method: id ? "PUT" : "POST", body });
      showMessage(id ? "Cliente actualizado" : "Cliente registrado");
      resetForm();
      await loadClients();
    });
  });
  field("cancel-btn").addEventListener("click", resetForm);
  field("search-form").addEventListener("submit", e => { e.preventDefault(); guarded(loadClients); });
  field("clients-body").addEventListener("click", e => {
    if (!e.target.dataset.edit) return;
    const c = window.currentClients.find(x => x.id === Number(e.target.dataset.edit));
    field("client-id").value = c.id;
    field("cedula").value = c.cedula; field("name").value = c.name;
    field("phone").value = c.phone || ""; field("email").value = c.email || "";
    field("form-title").textContent = `Editar cliente ${c.name}`;
    field("cancel-btn").hidden = false;
    field("cedula").focus();
  });
}
init();
