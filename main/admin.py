from django.contrib import admin
from .models import (
    Category, Product, ProductImage,
    Review, Cart, CartItem,
    ShippingAddress, Order, OrderItem
)

# Inline for Product Images
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "is_active", "created_at")
    list_filter = ("is_active", "category", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("custom_id", "user", "status", "total_amount", "is_paid", "created_at")
    list_filter = ("status", "is_paid", "created_at")
    search_fields = ("custom_id", "user__email")
    inlines = [OrderItemInline]


admin.site.register(Review)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(ShippingAddress)