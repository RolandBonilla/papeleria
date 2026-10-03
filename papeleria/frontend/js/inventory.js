let session;
const field = id => document.getElementById(id);

async function loadInventory() {
  const status = field("filter-status").value;
  const items = await api(`/inventory${status ? `?status=${encodeURIComponent(status)}` : ""}`);
  field("inventory-body").innerHTML = items.length ? items.map(i => `
    <tr><td>${esc(i.code)}</td><td>${esc(i.name)}</td><td class="num">${i.stock}</td>
    <td class="num">${i.min_stock}</td><td>${statusBadge(i.stock_status)}</td></tr>`).join("")
    : '<tr><td colspan="5" class="empty">No hay productos con ese estado.</td></tr>';
}

async function loadAlerts() {
  const alerts = await api("/inventory/alerts");
  field("alerts").innerHTML = alerts.length ? alerts.map(a => `<li>${esc(a.message)}</li>`).join("")
    : '<li class="empty" style="border-left-color:var(--ok);background:#f1faf5">No hay alertas de stock.</li>';
}

async function loadProductOptions() {
  fillSelect(field("entry-product"), await api("/products"), p => `${p.code} - ${p.name} (stock ${p.stock})`);
}

async function refresh() { await Promise.all([loadInventory(), loadAlerts(), loadProductOptions()]); }

async function init() {
  session = requireLogin();
  if (!session) return;
  field("entry-panel").hidden = !hasRole(session, "ADMINISTRADOR", "INVENTARIO");
  await guarded(refresh);
  field("filter-status").addEventListener("change", () => guarded(loadInventory));
  field("entry-form").addEventListener("submit", e => {
    e.preventDefault();
    guarded(async () => {
      const item = await api("/inventory/entries", { method: "POST", body: {
        product_id: Number(field("entry-product").value), quantity: Number(field("entry-quantity").value),
        note: field("entry-note").value.trim() || null,
      } });
      showMessage(`Ingreso registrado. ${item.name} ahora tiene ${item.stock} unidades.`);
      field("entry-form").reset();
      await refresh();
    });
  });
}
init();
