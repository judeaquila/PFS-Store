from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "user", "amount", "verified", "created_at")
    list_filter = ("verified", "created_at")
    search_fields = ("order__custom_id", "user__email", "ref")