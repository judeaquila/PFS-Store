import secrets
from django.conf import settings
from django.db import models
from decimal import Decimal
from main.models import Order

class Payment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    ref = models.CharField(max_length=200, unique=True)
    email = models.EmailField()
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.ref:
            self.ref = secrets.token_urlsafe(40)
        super().save(*args, **kwargs)

    def amount_value(self):
        return int(self.amount * Decimal("100"))

    def __str__(self):
        return f"Payment for Order #{self.order.id}"