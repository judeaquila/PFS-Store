from django.contrib.auth.views import LoginView
from .forms import EmailAuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
from main.models import Order, Product, Batch, OrderItem, Category
from django.http import JsonResponse
from main.forms import ProductForm, BatchForm
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from accounts.models import CustomUser, CompanySettings
from django.db.models import Sum, Count
from datetime import date, timedelta
from payments.models import Payment


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
def admin_dashboard(request):
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


# @staff_member_required
def dashboard_view(request):
    total_sales = Payment.objects.filter(verified=True).aggregate(total=Sum('amount'))['total'] or 0
    total_orders = Order.objects.count()
    new_customers = CustomUser.objects.filter(is_staff=False, date_joined__gte=date.today()-timedelta(days=30)).count()
    low_stock = Product.objects.filter(stock__lte=10).count()

    context = {
        "total_sales": total_sales,
        "total_orders": total_orders,
        "new_customers": new_customers,
        "low_stock": low_stock,
    }
    return render(request, "accounts/dashboard.html", context)

def products(request):
    return render(request, 'accounts/admin-products.html')

def orders(request):
    return render(request, 'accounts/admin-orders.html')

def inventory(request):
    return render(request, 'accounts/inventory.html')

def customers(request):
    return render(request, 'accounts/customers.html')

def reports(request):
    return render(request, 'accounts/reports.html')

def settings(request):
    return render(request, 'accounts/settings.html')


# @staff_member_required
def inventory_view(request):
    products = Product.objects.all()
    batches = Batch.objects.select_related('product').all()
    context = {"products": products, "batches": batches}
    return render(request, "accounts/inventory.html", context)

# -------------------- Product CRUD --------------------

# @staff_member_required
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            row_html = render_to_string("accounts/partials/product_row.html", {"product": product})
            return JsonResponse({"success": True, "row_html": row_html})
    return JsonResponse({"success": False, "errors": form.errors})

# @staff_member_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save()
            row_html = render_to_string("accounts/partials/product_row.html", {"product": product})
            return JsonResponse({"success": True, "row_html": row_html})
    else:
        form = ProductForm(instance=product)
    return render(request, "accounts/partials/product_form.html", {"form": form, "product": product})

# @staff_member_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return JsonResponse({"success": True})


# -------------------- Batch CRUD --------------------

# @staff_member_required
def add_batch(request):
    if request.method == "POST":
        form = BatchForm(request.POST)
        if form.is_valid():
            batch = form.save()
            row_html = render_to_string("accounts/partials/batch_row.html", {"batch": batch})
            return JsonResponse({"success": True, "row_html": row_html})
    return JsonResponse({"success": False, "errors": form.errors})

# @staff_member_required
def edit_batch(request, pk):
    batch = get_object_or_404(Batch, pk=pk)
    if request.method == "POST":
        form = BatchForm(request.POST, instance=batch)
        if form.is_valid():
            batch = form.save()
            row_html = render_to_string("accounts/partials/batch_row.html", {"batch": batch})
            return JsonResponse({"success": True, "row_html": row_html})
    else:
        form = BatchForm(instance=batch)
    return render(request, "accounts/partials/batch_form.html", {"form": form, "batch": batch})

# @staff_member_required
def delete_batch(request, pk):
    batch = get_object_or_404(Batch, pk=pk)
    batch.delete()
    return JsonResponse({"success": True})