// =======================================
//  CARRINHO
// =======================================

let cart = [];

function loadProducts() {
  fetch("/api/products")
    .then(r => r.json())
    .then(products => {
      const catalog = document.getElementById("catalog");
      catalog.innerHTML = "";

      products.forEach((p) => {
        const card = document.createElement("article");
        card.className = "card";

        card.innerHTML = `
          <img src="/static/img/${p.image}" alt="${p.name}">
          <div class="card-body">
            <div class="card-title">
              <div>
                <strong>${p.name}</strong>
                <div class="small muted">${p.description || ""}</div>
              </div>
              <div class="price">R$ ${Number(p.price).toFixed(2)}</div>
            </div>

            <div class="card-actions">
              <button class="btn btn-primary"
                onclick='addToCart(${p.id}, "${p.name.replace(/"/g, '\\"')}", ${p.price}, "${p.image}")'>
                Adicionar
              </button>
            </div>
          </div>
        `;

        catalog.appendChild(card);
      });
    });
}

function addToCart(id, name, price, image) {
  const found = cart.find((i) => i.id === id);
  if (found) found.qty++;
  else cart.push({ id, name, price, qty: 1, image });

  renderCart();
}

function renderCart() {
  const list = document.getElementById("cartList");
  list.innerHTML = "";

  let total = 0;

  cart.forEach((item) => {
    const div = document.createElement("div");
    div.className = "cart-item";

    div.innerHTML = `
      <img class="item-thumb" src="/static/img/${item.image}">
      
      <div style="flex:1">
        <div><strong>${item.name}</strong></div>
        <div class="small muted">${item.qty} x R$ ${item.price.toFixed(2)}</div>
      </div>

      <div>
        <button onclick="changeQty(${item.id}, 1)">➕</button>
        <button onclick="changeQty(${item.id}, -1)">➖</button>
        <button onclick="removeFromCart(${item.id})">Remover</button>
      </div>
    `;

    list.appendChild(div);

    total += item.qty * item.price;
  });

  document.getElementById("cartTotal").textContent = `R$ ${total.toFixed(2)}`;
}

function changeQty(id, delta) {
  const item = cart.find((i) => i.id === id);
  if (!item) return;

  item.qty += delta;
  if (item.qty <= 0) removeFromCart(id);

  renderCart();
}

function removeFromCart(id) {
  cart = cart.filter((i) => i.id !== id);
  renderCart();
}

// =======================================
//  PAGAMENTO — MOSTRAR E ESCONDER CAMPOS
// =======================================

const paymentSelect = document.getElementById("paymentMethod");
const paymentCashBox = document.getElementById("paymentCashBox");
const paymentCardBox = document.getElementById("paymentCardBox");
const paymentPixBox = document.getElementById("paymentPixBox");

const cashNeedChange = document.getElementById("cashNeedChange");
const cashAmount = document.getElementById("cashAmount");

const pixComprovante = document.getElementById("pixComprovante");
const generatePixBtn = document.getElementById("generatePixBtn");
const pixQrPreview = document.getElementById("pixQrPreview");

const btnCheckout = document.getElementById("btnCheckout");


// ocultar tudo ao carregar
paymentCashBox.classList.add("hidden");
paymentCardBox.classList.add("hidden");
paymentPixBox.classList.add("hidden");

btnCheckout.disabled = true;

// Seleção de método de pagamento
paymentSelect.addEventListener("change", () => {
  paymentCashBox.classList.add("hidden");
  paymentCardBox.classList.add("hidden");
  paymentPixBox.classList.add("hidden");

  btnCheckout.disabled = true;

  const method = paymentSelect.value;

  if (method === "dinheiro") {
    paymentCashBox.classList.remove("hidden");
  }

  if (method === "cartao") {
    paymentCardBox.classList.remove("hidden");
    btnCheckout.disabled = false;
  }

  if (method === "pix") {
    paymentPixBox.classList.remove("hidden");
  }
});

// Mostrar campo "Troco para quanto"
cashNeedChange.addEventListener("change", () => {
  if (cashNeedChange.value === "sim") {
    cashAmount.classList.remove("hidden");
  } else {
    cashAmount.classList.add("hidden");
    cashAmount.value = "";
  }
});

// Formatar campo Troco para quanto em moeda BRL
cashAmount.addEventListener("input", () => {
  let v = cashAmount.value.replace(/\D/g, "");

  if (v.length === 0) {
    cashAmount.value = "";
    return;
  }

  v = (parseInt(v) / 100).toFixed(2);

  cashAmount.value = "R$ " + v.replace(".", ",");
});


// liberar botão se digitou troco
cashAmount.addEventListener("input", () => {
  if (paymentSelect.value === "dinheiro" && cashAmount.value.trim() !== "") {
    btnCheckout.disabled = false;
  }
});

// liberar botão ao enviar comprovante PIX
pixComprovante.addEventListener("change", () => {
  if (pixComprovante.files.length > 0) {
    btnCheckout.disabled = false;
  }
});


// =======================================
// GERAR QR CODE PIX (USANDO PAYLOAD REAL)
// =======================================

generatePixBtn.addEventListener("click", () => {

  const chavePix = "71991118924";
  const recebedor = "Josenilton Santos da Cruz";
  const banco = "C6 Bank";  // <-- coloque sua chave real aqui

  const qrUrl =
    "https://api.qrserver.com/v1/create-qr-code/?size=240x240&data=" +
    encodeURIComponent(chavePix);

  pixQrPreview.classList.remove("hidden");

  pixQrPreview.innerHTML = `
    <img src="${qrUrl}" width="200" height="200" style="border-radius:8px;">
    <p style="font-size:12px;margin-top:6px;">Chave PIX:</p>
    <textarea readonly style="width:100%;height:60px;font-size:12px;">Chave: ${chavePix}
Banco: ${banco}
Recebedor: ${recebedor}</textarea>
  `;
});




// =======================================
//  FINALIZAR PEDIDO
// =======================================

document.getElementById("btnCheckout").addEventListener("click", function () {

  const name = document.getElementById("customerName").value.trim();
  const address = document.getElementById("customerAddress").value.trim();
  const contact = document.getElementById("customerContact").value.trim();
  const note = document.getElementById("customerNote").value.trim();
  const bairro = document.getElementById("customerBairro").value;
  const payment = paymentSelect.value;

  if (!name || !address) return alert("Preencha nome e endereço!");
  if (cart.length === 0) return alert("Seu carrinho está vazio!");
  if (!bairro) return alert("Selecione o bairro!");
  if (!payment) return alert("Selecione o método de pagamento!");

  let comprovanteFile = null;

  if (payment === "pix") {
    if (!pixComprovante.files || !pixComprovante.files[0]) {
      alert("Envie o comprovante PIX.");
      return;
    }
    comprovanteFile = pixComprovante.files[0];
  }

  const formData = new FormData();
  formData.append("customer_name", name);
  formData.append("customer_address", address);
  formData.append("customer_contact", contact);
  formData.append("customer_note", note);
  formData.append("bairro", bairro);
  formData.append("payment_method", payment);

  if (payment === "dinheiro") {
    formData.append("troco_para", cashAmount.value.trim());
  }

  if (comprovanteFile) {
    formData.append("pix_comprovante", comprovanteFile);
  }

  formData.append("cart", JSON.stringify(cart));

  fetch("/api/checkout", { method: "POST", body: formData })
    .then(r => r.json())
    .then(json => {
      if (json.ok && json.whatsapp_url) {
        window.open(json.whatsapp_url, "_blank");
      } else {
        alert("Erro ao gerar pedido.");
      }
    });
});

// Inicializar
loadProducts();
renderCart();
