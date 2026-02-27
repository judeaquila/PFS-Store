from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView, register_view, dashboard_view, order_history_view, order_detail_view, admin_dashboard, products, orders, inventory, customers, reports, settings, add_product, edit_product, delete_product, add_batch, edit_batch, delete_batch

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="product_list"), name="logout"),
    path("register/", register_view, name="register"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("orders/", order_history_view, name="order_history"),
    path("orders/<int:order_id>/", order_detail_view, name="order_detail"),

    # DASHBOARD
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/products/', products, name='products'),
    path('admin-dashboard/orders/', orders, name='orders'),
    path('admin-dashboard/inventory/', inventory, name='inventory'),
    path('admin-dashboard/customers/', customers, name='customers'),
    path('admin-dashboard/reports/', reports, name='reports'),
    path('admin-dashboard/settings/', settings, name='settings'),
    # Inventory CRUD
    path('inventory/add_product/', add_product, name='add_product'),
    path('inventory/edit_product/<int:pk>/', edit_product, name='edit_product'),
    path('inventory/delete_product/<int:pk>/', delete_product, name='delete_product'),
    path('inventory/add_batch/', add_batch, name='add_batch'),
    path('inventory/edit_batch/<int:pk>/', edit_batch, name='edit_batch'),
    path('inventory/delete_batch/<int:pk>/', delete_batch, name='delete_batch'),

]
