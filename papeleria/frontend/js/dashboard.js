async function init() {
  if (!requireLogin()) return;
  await guarded(async () => {
    const [summary, alerts] = await Promise.all([api("/reports/dashboard"), api("/inventory/alerts")]);
    document.getElementById("stat-products").textContent = summary.total_products;
    document.getElementById("stat-low").textContent = summary.low_stock_products;
    document.getElementById("stat-sales").textContent = summary.sales_today;
    document.getElementById("stat-total").textContent = money(summary.total_sold_today);
    document.getElementById("alerts").innerHTML = alerts.length
      ? alerts.map(a => `<li>${esc(a.message)}</li>`).join("")
      : '<li class="empty" style="border-left-color:var(--ok);background:#f1faf5">No hay alertas de stock.</li>';
  });
}
init();
