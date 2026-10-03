let products = []; let cart = [];
const field = id => document.getElementById(id);
const cents = value => Math.round(Number(value) * 100);

function renderCart() {
  let totalCents = 0;
  field("cart-body").innerHTML = cart.length ? cart.map((line, index) => {
    const subtotal = cents(line.product.price) * line.quantity;
    totalCents += subtotal;
    return `<tr><td>${esc(line.product.name)}</td><td class="num">${line.quantity}</td>
      <td class="num">${money(line.product.price)}</td><td class="num">${money(subtotal / 100)}</td>
      <td><button type="button" class="danger small" data-remove="${index}">Quitar</button></td></tr>`;
  }).join("") : '<tr><td colspan="5" class="empty">Agregue productos a la venta.</td></tr>';
  field("total").textContent = money(totalCents / 100);
  field("register-btn").disabled = cart.length === 0;
}

function addToCart() {
  const product = products.find(p => p.id === Number(field("product").value));
  const quantity = Number(field("quantity").value);
  if (!product) throw new Error("Seleccione un producto");
  if (!Number.isInteger(quantity) || quantity <= 0) throw new Error("La cantidad debe ser un entero mayor que cero");
  const line = cart.find(l => l.product.id === product.id);
  const inCart = line ? line.quantity : 0;
  if (inCart + quantity > product.stock) throw new Error(`Stock insuficiente de ${product.name}: disponible ${product.stock}`);
  if (line) line.quantity += quantity; else cart.push({ product, quantity });
  field("quantity").value = 1;
  renderCart();
}

async function loadData() {
  const [clients, loaded] = await Promise.all([api("/clients"), api("/products")]);
  products = loaded;
  fillSelect(field("client"), clients, c => `${c.name} (${c.cedula})`, "Sin cliente (consumidor final)");
  fillSelect(field("product"), products, p => `${p.code} - ${p.name} - ${money(p.price)} - stock ${p.stock}`);
  [...field("product").options].forEach((option, i) => { option.disabled = products[i].stock === 0; });
}

async function registerSale() {
  const body = {
    client_id: field("client").value ? Number(field("client").value) : null,
    items: cart.map(l => ({ product_id: l.product.id, quantity: l.quantity })),
  };
  const sale = await api("/sales", { method: "POST", body });
  showMessage(`Venta #${sale.id} registrada. Total: ${money(sale.total)}. El inventario fue actualizado.`);
  cart = [];
  renderCart();
  await loadData();
}

async function init() {
  const session = requireLogin();
  if (!session) return;
  await guarded(loadData);
  renderCart();
  field("add-form").addEventListener("submit", e => { e.preventDefault(); guarded(async () => addToCart()); });
  field("register-btn").addEventListener("click", () => guarded(registerSale));
  field("cart-body").addEventListener("click", e => {
    if (e.target.dataset.remove === undefined) return;
    cart.splice(Number(e.target.dataset.remove), 1);
    renderCart();
  });
}
init();
