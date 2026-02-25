from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView, register_view, dashboard_view, order_history_view, order_detail_view

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="product_list"), name="logout"),
    path("register/", register_view, name="register"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("orders/", order_history_view, name="order_history"),
    path("orders/<int:order_id>/", order_detail_view, name="order_detail"),
]
