from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ShippingAddress, Order, OrderItem, CartItem
from .models import Cart
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.conf import settings
from payments.models import Payment
from django.http import JsonResponse
from django.views.decorators.http import require_POST



def index(request):
    products = Product.objects.filter(is_active=True)[:6]
    return render(request, "main/index.html", {"products": products})


def product_list(request):
    products = Product.objects.filter(is_active=True)
    return render(request, "main/products.html", {"products": products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, "main/product_detail.html", {"product": product})


def get_user_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


import json
from django.views.decorators.http import require_POST
from django.db.models import Sum

@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.stock < 1:
        return JsonResponse({"error": "Out of stock"}, status=400)

    # Read quantity from JSON
    data = json.loads(request.body)
    quantity = int(data.get("quantity", 1))

    if quantity < 1:
        quantity = 1

    if quantity > product.stock:
        quantity = product.stock

    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if item_created:
        cart_item.quantity = quantity
    else:
        new_quantity = cart_item.quantity + quantity

        # Prevent exceeding stock
        if new_quantity > product.stock:
            new_quantity = product.stock

        cart_item.quantity = new_quantity

    cart_item.save()

    # Cart count using DB aggregation
    total_quantity = cart.items.aggregate(
        total=Sum("quantity")
    )["total"] or 0

    return JsonResponse({
        "success": True,
        "cart_count": total_quantity
    })


@login_required
def remove_from_cart(request, product_id):
    cart = get_user_cart(request.user)
    cart_item = get_object_or_404(
        CartItem,
        cart=cart,
        product_id=product_id
    )
    cart_item.delete()
    return redirect("cart_detail")


@login_required
def update_cart(request, product_id, action):
    cart = get_user_cart(request.user)
    cart_item = get_object_or_404(
        CartItem,
        cart=cart,
        product_id=product_id
    )

    if action == "increase":
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1

    elif action == "decrease":
        cart_item.quantity -= 1
        if cart_item.quantity <= 0:
            cart_item.delete()
            return redirect("cart_detail")

    cart_item.save()
    return redirect("cart_detail")


@login_required
def cart_detail(request):
    cart = get_user_cart(request.user)
    items = cart.items.select_related("product")

    subtotal = Decimal("0.00")

    for item in items:
        subtotal += item.get_total_price()

    shipping = Decimal("5.00")
    total = subtotal + shipping

    return render(request, "main/cart.html", {
        "cart": cart,
        "cart_items": items,
        "subtotal": subtotal,
        "shipping": shipping,
        "total": total,
    })


@login_required
@transaction.atomic
def checkout(request):

    cart = get_user_cart(request.user)
    items = cart.items.select_related("product")

    if not items.exists():
        return redirect("cart_detail")

    subtotal = Decimal("0.00")

    for item in items:
        if item.quantity > item.product.stock:
            return redirect("cart_detail")
        subtotal += item.get_total_price()

    shipping = Decimal("5.00")
    grand_total = subtotal + shipping

    if request.method == "POST":

        shipping_address = ShippingAddress.objects.create(
            user=request.user,
            address_line_1=request.POST.get("address"),
            city=request.POST.get("city"),
            state=request.POST.get("state", ""),
            phone_number=request.POST.get("phone_number"),
            country=request.POST.get("country", "")
        )

        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            total_amount=grand_total,
            status="pending"
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        payment = Payment.objects.create(
            user=request.user,
            order=order,
            amount=grand_total,
            email=request.user.email
        )

        return render(request, "payments/make_payment.html", {
            "payment": payment,
            "paystack_pub_key": settings.PAYSTACK_PUBLIC_KEY,
            "amount_value": payment.amount_value(),
        })

    return render(request, "main/checkout.html", {
        "cart_items": items,
        "subtotal": subtotal,
        "shipping": shipping,
        "grand_total": grand_total,
    })

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "main/order_success.html", {"order": order})