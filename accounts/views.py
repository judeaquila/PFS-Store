from django.contrib.auth.views import LoginView
from .forms import EmailAuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
from main.models import Order


class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = EmailAuthenticationForm


def register_view(request):
    next_url = request.GET.get("next")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            return redirect(next_url or "product_list")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def dashboard_view(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")

    context = {
        "orders_count": orders.count(),
        "recent_orders": orders[:5],
    }

    return render(request, "accounts/dashboard.html", context)


@login_required
def order_history_view(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "accounts/order_history.html", {
        "orders": orders
    })


@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(request, "accounts/order_detail.html", {
        "order": order
    })