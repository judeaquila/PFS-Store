from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ShippingAddress, Order, OrderItem
from .cart import Cart
from django.http import JsonResponse
import json
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.db import transaction

def index(request):
    products = Product.objects.filter(is_active=True)[:6]
    return render(request, "main/index.html", {"products": products})


def product_list(request):
    products = Product.objects.filter(is_active=True)
    return render(request, "main/products.html", {"products": products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, "main/product_detail.html", {"product": product})


def add_to_cart(request, product_id):
    if request.method == "POST":
        data = json.loads(request.body)
        quantity = int(data.get("quantity", 1))

        product = get_object_or_404(Product, id=product_id)

        if quantity > product.stock:
            return JsonResponse({
                "error": "Not enough stock"
            }, status=400)

        cart = request.session.get("cart", {})

        if str(product_id) in cart:
            cart[str(product_id)] += quantity
        else:
            cart[str(product_id)] = quantity

        # Optional: prevent exceeding stock in cart
        if cart[str(product_id)] > product.stock:
            cart[str(product_id)] = product.stock

        request.session["cart"] = cart

        return JsonResponse({
            "cart_count": sum(cart.values())
        })


def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session["cart"] = cart
    return redirect("cart_detail")


def update_cart(request, product_id, action):
    cart = request.session.get("cart", {})
    product_id = str(product_id)

    if product_id in cart:
        if action == "increase":
            cart[product_id] += 1

        elif action == "decrease":
            cart[product_id] -= 1

        if cart[product_id] <= 0:
            del cart[product_id]

    request.session["cart"] = cart
    return redirect("cart_detail")


def cart_detail(request):
    session_cart = request.session.get("cart", {})
    cart_items = []
    total_price = 0

    for product_id, quantity in session_cart.items():
        product = get_object_or_404(Product, id=product_id)

        item_total = product.price * quantity
        total_price += item_total

        cart_items.append({
            "product": product,
            "name": product.name,
            "image": product.get_main_image_url(),
            "price": product.price,
            "quantity": quantity,
            "total_price": item_total
        })

    context = {
        "cart_items": cart_items,
        "total_price": total_price
    }

    return render(request, "main/cart.html", context)


@login_required
@transaction.atomic
def checkout(request):
    session_cart = request.session.get("cart", {})

    if not session_cart:
        return redirect("cart_detail")

    cart_items = []
    subtotal = Decimal("0.00")

    for product_id, quantity in session_cart.items():
        product = get_object_or_404(Product, id=product_id)

        # Prevent overselling
        if quantity > product.stock:
            return redirect("cart_detail")

        item_total = product.price * quantity
        subtotal += item_total

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "total": item_total
        })

    shipping = Decimal("5.00")
    grand_total = subtotal + shipping

    # =========================
    # HANDLE POST (Place Order)
    # =========================
    if request.method == "POST":

        # Create Shipping Address
        shipping_address = ShippingAddress.objects.create(
            user=request.user,
            address_line_1=request.POST.get("address"),
            city=request.POST.get("city"),
            state=request.POST.get("state", ""),
            postal_code=request.POST.get("postal_code"),
            country=request.POST.get("country", "Nigeria")
        )

        # Create Order
        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            total_amount=grand_total,
            status="pending"
        )

        # Create Order Items + Deduct Stock
        for item in cart_items:
            product = item["product"]
            quantity = item["quantity"]

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )

            # Deduct stock
            product.stock -= quantity
            product.save()

        # Clear session cart
        request.session["cart"] = {}

        # Redirect to success page
        return redirect("order_success", order_id=order.id)

    context = {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "shipping": shipping,
        "grand_total": grand_total
    }

    return render(request, "main/checkout.html", context)


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "main/order_success.html", {"order": order})