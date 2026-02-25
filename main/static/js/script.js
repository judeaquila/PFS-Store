let cart = JSON.parse(localStorage.getItem("cart")) || [];

// PAGE LOAD FADE
document.addEventListener("DOMContentLoaded", () => {
  document.body.classList.add("loaded");
  updateCartBadge();
  renderCart();
});

// SAVE CART
function saveCart() {
  localStorage.setItem("cart", JSON.stringify(cart));
  updateCartBadge();
}

// ADD TO CART
function addToCart(id, name, price, image) {
  const existing = cart.find((item) => item.id === id);

  if (existing) {
    existing.quantity++;
  } else {
    cart.push({ id, name, price, image, quantity: 1 });
  }

  saveCart();
  showToast("Product added to cart");
}

// REMOVE ITEM
function removeFromCart(id) {
  cart = cart.filter((item) => item.id !== id);
  saveCart();
  renderCart();
}

// CHANGE QUANTITY
function changeQty(id, amount) {
  const item = cart.find((i) => i.id === id);
  if (!item) return;

  item.quantity += amount;

  if (item.quantity <= 0) {
    removeFromCart(id);
  } else {
    saveCart();
    renderCart();
  }
}

// UPDATE BADGE
function updateCartBadge() {
  const badge = document.getElementById("cart-count");
  if (!badge) return;

  const total = cart.reduce((sum, item) => sum + item.quantity, 0);
  badge.innerText = total;
}

// RENDER CART
function renderCart() {
  const table = document.getElementById("cart-items");
  const totalEl = document.getElementById("cart-total");
  if (!table) return;

  table.innerHTML = "";
  let total = 0;

  cart.forEach((item) => {
    total += item.price * item.quantity;

    table.innerHTML += `
        <tr>
            <td>${item.name}</td>
            <td>$${item.price}</td>
            <td>
                <button class="qty-btn" onclick="changeQty(${item.id}, -1)">-</button>
                ${item.quantity}
                <button class="qty-btn" onclick="changeQty(${item.id}, 1)">+</button>
            </td>
            <td>$${(item.price * item.quantity).toFixed(2)}</td>
            <td><button class="btn btn-sm btn-danger" onclick="removeFromCart(${item.id})">X</button></td>
        </tr>`;
  });

  if (totalEl) totalEl.innerText = total.toFixed(2);
}

// TOAST
function showToast(message) {
  const toastEl = document.getElementById("liveToast");
  const toastBody = document.getElementById("toast-body");

  toastBody.innerText = message;

  const toast = new bootstrap.Toast(toastEl);
  toast.show();
}

// SEARCH & FILTER
function filterProducts() {
  const search = document.getElementById("searchInput").value.toLowerCase();
  const cards = document.querySelectorAll(".product-card");

  cards.forEach((card) => {
    const name = card.dataset.name.toLowerCase();
    card.style.display = name.includes(search) ? "block" : "none";
  });
}
