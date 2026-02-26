from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from main.models import Cart, Order, OrderItem, ShippingAddress
from main.views import get_user_cart
from .models import Payment
from .paystack import Paystack


@login_required
def initiate_checkout(request):
    cart = Cart.objects.get(user=request.user)

    if not cart.items.exists():
        return redirect("cart")

    if request.method == "POST":

        # Create shipping address
        shipping = ShippingAddress.objects.create(
            user=request.user,
            address_line_1=request.POST['address_line_1'],
            city=request.POST['city'],
            state=request.POST['state'],
            phone_number=request.POST['phone_number'],
            country=request.POST['country'],
        )

        # Create order
        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping,
            total_amount=0
        )

        total = Decimal("0.00")

        # Create order items
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            total += item.get_total_price()

        order.total_amount = total
        order.save()

        # Create payment record
        payment = Payment.objects.create(
            user=request.user,
            order=order,
            amount=total,
            email=request.user.email
        )

        context = {
            "order": order,
            "payment": payment,
            "paystack_pub_key": settings.PAYSTACK_PUBLIC_KEY,
            "amount_value": payment.amount_value(),
        }

        return render(request, "payments/make_payment.html", context)

    return redirect("checkout")


@login_required
def verify_payment(request, ref):

    payment = get_object_or_404(Payment, ref=ref, user=request.user)

    if payment.verified:
        return redirect("order_detail", order_id=payment.order.id)

    paystack = Paystack()
    status, result = paystack.verify_payment(ref)

    if status and result["status"] == "success":

        if result["amount"] / 100 == float(payment.amount):

            payment.verified = True
            payment.save()

            order = payment.order
            order.is_paid = True
            order.status = "processing"
            order.save()

            # Deduct stock
            for item in order.items.all():
                product = item.product
                product.stock -= item.quantity
                product.save()

            # Clear database cart
            cart = get_user_cart(request.user)
            cart.items.all().delete()

            return redirect("order_detail", order_id=order.id)

    return redirect("checkout")