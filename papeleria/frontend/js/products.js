let session; let categories = [];
const form = document.getElementById("product-form");
const field = id => document.getElementById(id);

function resetForm() {
  form.reset();
  field("product-id").value = "";
  field("stock").disabled = false;
  field("form-title").textContent = "Registrar producto";
  field("cancel-btn").hidden = true;
}

async function loadProducts() {
  const params = new URLSearchParams();
  if (field("search-q").value.trim()) params.set("q", field("search-q").value.trim());
  if (field("search-category").value) params.set("category_id", field("search-category").value);
  const products = await api(`/products?${params}`);
  const canEdit = hasRole(session, "ADMINISTRADOR", "INVENTARIO");
  field("products-body").innerHTML = products.length ? products.map(p => `
    <tr><td>${esc(p.code)}</td><td>${esc(p.name)}</td><td>${esc(p.category_name)}</td>
    <td class="num">${money(p.price)}</td><td class="num">${p.stock}</td><td class="num">${p.min_stock}</td>
    <td>${canEdit ? `<button class="secondary small" data-edit="${p.id}">Editar</button>
      <button class="danger small" data-delete="${p.id}">Eliminar</button>` : ""}</td></tr>`).join("")
    : '<tr><td colspan="7" class="empty">No se encontraron productos.</td></tr>';
  window.currentProducts = products;
}

function startEdit(id) {
  const p = window.currentProducts.find(x => x.id === id);
  field("product-id").value = p.id;
  field("code").value = p.code;
  field("name").value = p.name;
  field("category").value = p.category_id;
  field("price").value = p.price;
  field("stock").value = p.stock;
  field("stock").disabled = true;
  field("min_stock").value = p.min_stock;
  field("form-title").textContent = `Editar producto ${p.code}`;
  field("cancel-btn").hidden = false;
  field("code").focus();
}

async function loadCategories() {
  categories = await api("/categories");
  fillSelect(field("category"), categories, c => c.name);
  fillSelect(field("search-category"), categories, c => c.name, "Todas");
}

async function init() {
  session = requireLogin();
  if (!session) return;
  const canEdit = hasRole(session, "ADMINISTRADOR", "INVENTARIO");
  field("form-panel").hidden = !canEdit;
  await guarded(async () => { await loadCategories(); await loadProducts(); });

  form.addEventListener("submit", event => {
    event.preventDefault();
    guarded(async () => {
      const id = field("product-id").value;
      const body = {
        code: field("code").value, name: field("name").value, category_id: Number(field("category").value),
        price: field("price").value, min_stock: Number(field("min_stock").value),
      };
      if (id) await api(`/products/${id}`, { method: "PUT", body });
      else await api("/products", { method: "POST", body: { ...body, stock: Number(field("stock").value) } });
      showMessage(id ? "Producto actualizado" : "Producto registrado");
      resetForm();
      await loadProducts();
    });
  });
  field("cancel-btn").addEventListener("click", resetForm);
  field("search-form").addEventListener("submit", e => { e.preventDefault(); guarded(loadProducts); });
  field("category-form").addEventListener("submit", e => {
    e.preventDefault();
    guarded(async () => {
      await api("/categories", { method: "POST", body: { name: field("category-name").value } });
      field("category-name").value = "";
      await loadCategories();
      showMessage("Categoría agregada");
    });
  });
  field("products-body").addEventListener("click", e => {
    const edit = e.target.dataset.edit; const del = e.target.dataset.delete;
    if (edit) startEdit(Number(edit));
    if (del && confirm("¿Eliminar este producto? Se conserva el historial de ventas.")) {
      guarded(async () => { await api(`/products/${del}`, { method: "DELETE" }); showMessage("Producto eliminado"); await loadProducts(); });
    }
  });
}
init();
