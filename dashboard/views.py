from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import logout
from django.db.models import Sum
from datetime import timedelta
from main.models import Order, Product, OrderItem, Category, ProductImage
from accounts.models import CustomUser
from payments.models import Payment
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@staff_member_required
def dashboard_home(request):
    categories = Category.objects.all()

    # Metric counts (same as before)
    total_sales = Order.objects.filter(is_paid=True).aggregate(total=Sum('total_amount'))['total'] or 0
    total_orders = Order.objects.count()
    total_products = Product.objects.count()
    total_users = CustomUser.objects.count()

    packaged_food_count = Product.objects.filter(category__name="Packaged Foods").count()
    packaged_material_count = Product.objects.filter(category__name="Packaged Materials").count()
    machinery_count = Product.objects.filter(category__name="Machinery").count()

    recent_orders = Order.objects.order_by('-created_at')[:5]

    # ----- Daily Data for last 7 days -----
    today = timezone.now().date()
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    daily_labels = [d.strftime('%b %d') for d in last_7_days]

    daily_sales = []
    daily_orders = []

    for day in last_7_days:
        day_orders = Order.objects.filter(is_paid=True, created_at__date=day)
        daily_sales.append(float(day_orders.aggregate(total=Sum('total_amount'))['total'] or 0))
        daily_orders.append(day_orders.count())

    # ----- Weekly Data: last 4 weeks (Monday-Sunday) -----
    # Find the start of the current week (Monday)
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())

    weekly_labels = []
    weekly_sales = []
    weekly_orders = []

    for i in range(3, -1, -1):  # last 4 weeks
        week_start = start_of_week - timedelta(weeks=i)
        week_end = week_start + timedelta(days=6)
        week_orders = Order.objects.filter(is_paid=True, created_at__date__range=(week_start, week_end))
        
        weekly_labels.append(f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d')}")
        weekly_sales.append(float(week_orders.aggregate(total=Sum('total_amount'))['total'] or 0))
        weekly_orders.append(week_orders.count())

        # ----- Monthly Data for last 6 months -----
        monthly_labels = []
        monthly_sales = []
        monthly_orders = []

    for i in range(5, -1, -1):
        month = (today.replace(day=1) - timedelta(days=i*30))
        month_start = month.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        month_orders = Order.objects.filter(is_paid=True, created_at__date__range=(month_start, month_end))
        monthly_labels.append(month_start.strftime('%b %Y'))
        monthly_sales.append(float(month_orders.aggregate(total=Sum('total_amount'))['total'] or 0))
        monthly_orders.append(month_orders.count())

    # Low stock: products with stock <= 5
    low_stock_products = Product.objects.filter(stock__lte=5).order_by('stock')[:5]

    # Top-selling products: sum of quantity in completed or paid orders
    top_products = (OrderItem.objects
                    .filter(order__is_paid=True)
                    .values('product__name')
                    .annotate(total_sold=Sum('quantity'))
                    .order_by('-total_sold')[:5])

    context = {
        'categories': categories,
        'total_sales': total_sales,
        'total_orders': total_orders,
        'total_products': total_products,
        'total_users': total_users,
        'packaged_food_count': packaged_food_count,
        'packaged_material_count': packaged_material_count,
        'machinery_count': machinery_count,
        'recent_orders': recent_orders,
        'daily_labels': daily_labels,
        'daily_sales': daily_sales,
        'daily_orders': daily_orders,
        'weekly_labels': weekly_labels,
        'weekly_sales': weekly_sales,
        'weekly_orders': weekly_orders,
        'monthly_labels': monthly_labels,
        'monthly_sales': monthly_sales,
        'monthly_orders': monthly_orders,
        'low_stock_products': low_stock_products,
        'top_products': top_products,
    }

    return render(request, "dashboard/home.html", context)



@staff_member_required
def orders_list(request):
    orders = Order.objects.select_related('shipping_address').order_by('-created_at')

    # --- Filters ---
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    if search_query:
        orders = orders.filter(custom_id__icontains=search_query) 
    if status_filter:
        orders = orders.filter(status=status_filter)

    return render(request, "dashboard/orders_list.html", {
        "orders": orders,
        "search_query": search_query,
        "status_filter": status_filter,
    })


@staff_member_required
def order_detail(request, custom_id):
    order = get_object_or_404(Order, custom_id=custom_id)

    # Handle status update
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, "Order status updated successfully.")
            return redirect("dashboard_order_detail", custom_id=custom_id)

    # Get linked payment (OneToOne)
    payment = getattr(order, "payment", None)

    context = {
        "order": order,
        "payment": payment,
    }

    return render(request, "dashboard/order_detail.html", context)


@staff_member_required
def products_list(request):
    search_query = request.GET.get("q", "")
    category_id = request.GET.get("category", "")
    
    categories = Category.objects.all().order_by("name")
    products = Product.objects.all().order_by("-id")
    
    if search_query:
        products = products.filter(name__icontains=search_query)
    
    if category_id:
        products = products.filter(category__id=category_id)
    
    return render(request, "dashboard/products_list.html", {
        "products": products,
        "categories": categories,
        "search_query": search_query,
        "active_category": int(category_id) if category_id else None
    })


@staff_member_required
def add_product(request):
    categories = Category.objects.all()
    if request.method == "POST":
        name = request.POST.get("name")
        category_id = request.POST.get("category")
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        description = request.POST.get("description")
        image = request.FILES.get("image")
        category = Category.objects.get(id=category_id) if category_id else None

        product = Product.objects.create(
            name=name,
            category=category,
            price=price,
            stock=stock,
            description=description
        )
        if image:
            product_image = product.images.create(image=image, is_primary=True)
        messages.success(request, f"Product '{product.name}' added successfully!")
        return redirect("dashboard_products_list")

    return render(request, "dashboard/products_list.html", {"categories": categories})


@staff_member_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()

    if request.method == "POST":
        product.name = request.POST.get("name")
        category_id = request.POST.get("category")
        product.category = Category.objects.get(id=category_id) if category_id else None
        product.price = request.POST.get("price")
        product.stock = request.POST.get("stock")
        product.description = request.POST.get("description")
        image = request.FILES.get("image")
        if image:
            # replace primary image or add a new one
            ProductImage.objects.filter(product=product, is_primary=True).update(is_primary=False)
            product.images.create(image=image, is_primary=True)
        product.save()
        messages.success(request, f"Product '{product.name}' updated successfully!")
        return redirect("dashboard_products_list")

    return render(request, "dashboard/edit_product.html", {
        "product": product,
        "categories": categories
    })


@staff_member_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, f"Product '{product.name}' deleted successfully!")
    return redirect("dashboard_products_list")



@staff_member_required
def categories_list(request):
    search_query = request.GET.get("q", "")
    categories = Category.objects.all().order_by("name")

    if search_query:
        categories = categories.filter(name__icontains=search_query)

    return render(request, "dashboard/categories_list.html", {
        "categories": categories,
        "search_query": search_query
    })

@staff_member_required
def add_category(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            Category.objects.create(name=name)
            messages.success(request, f"Category '{name}' added successfully!")
    return redirect("dashboard_categories_list")


@staff_member_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            category.name = name
            category.save()
            messages.success(request, f"Category '{name}' updated successfully!")
    return redirect("dashboard_categories_list")


@staff_member_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    messages.success(request, f"Category '{category.name}' deleted successfully!")
    return redirect("dashboard_categories_list")


@staff_member_required
def users_list(request):
    users = CustomUser.objects.all().order_by('-id')
    return render(request, "dashboard/users_list.html", {"users": users})


@staff_member_required
def payments_list(request):
    payments = Payment.objects.select_related('order', 'user').order_by('-created_at')

    search_query = request.GET.get('search', '')
    verified_filter = request.GET.get('verified', '')

    if search_query:
        payments = payments.filter(ref__icontains=search_query)
    if verified_filter in ['yes', 'no']:
        payments = payments.filter(verified=(verified_filter == 'yes'))

    return render(request, "dashboard/payments_list.html", {
        "payments": payments,
        "search_query": search_query,
        "verified_filter": verified_filter,
    })


@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
    return redirect("index")