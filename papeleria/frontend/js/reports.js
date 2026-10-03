const field = id => document.getElementById(id);

async function loadSales() {
  const params = new URLSearchParams();
  if (field("date-from").value) params.set("date_from", field("date-from").value);
  if (field("date-to").value) params.set("date_to", field("date-to").value);
  try {
    const report = await api(`/reports/sales?${params}`);
    field("sales-body").innerHTML = report.sales.length ? report.sales.map(s => `
      <tr><td>${s.id}</td><td>${esc(formatDate(s.date))}</td><td>${esc(s.client_name || "Consumidor final")}</td>
      <td>${s.details.map(d => `${esc(d.product_name)} x${d.quantity}`).join(", ")}</td>
      <td class="num">${money(s.total)}</td></tr>`).join("")
      : '<tr><td colspan="5" class="empty">No hay ventas en el período.</td></tr>';
    field("sales-summary").textContent = `${report.count} ventas, total ${money(report.total)}`;
  } catch (error) {
    field("sales-body").innerHTML = `<tr><td colspan="5" class="empty">${esc(error.message)}</td></tr>`;
    field("sales-summary").textContent = "";
  }
}

async function loadLowStock() {
  const items = await api("/reports/low-stock");
  field("low-body").innerHTML = items.length ? items.map(i => `
    <tr><td>${esc(i.code)}</td><td>${esc(i.name)}</td><td class="num">${i.stock}</td>
    <td class="num">${i.min_stock}</td><td>${statusBadge(i.stock_status)}</td></tr>`).join("")
    : '<tr><td colspan="5" class="empty">Ningún producto tiene stock bajo.</td></tr>';
}

async function init() {
  if (!requireLogin()) return;
  await guarded(async () => { await Promise.all([loadSales(), loadLowStock()]); });
  field("filter-form").addEventListener("submit", e => { e.preventDefault(); loadSales(); });
}
init();
