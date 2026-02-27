from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_home, name="dashboard_home"),
    path('orders/', views.orders_list, name='dashboard_orders_list'),
    path("orders/<str:custom_id>/", views.order_detail, name="dashboard_order_detail"),

    path("products/", views.products_list, name="dashboard_products_list"),
    path('products/add/', views.add_product, name='dashboard_add_product'),
    path('products/edit/<int:product_id>/', views.edit_product, name="dashboard_edit_product"),
    path('products/delete/<int:product_id>/', views.delete_product, name="dashboard_delete_product"),


    path("categories/", views.categories_list, name="dashboard_categories_list"),
    path('categories/add/', views.add_category, name='dashboard_add_category'),
    path("categories/edit/<int:category_id>/", views.edit_category, name="dashboard_edit_category"),
    path("categories/delete/<int:category_id>/", views.delete_category, name="dashboard_delete_category"),

    path('users/', views.users_list, name='dashboard_users_list'),
    path('payments/', views.payments_list, name='dashboard_payments_list'),
]
