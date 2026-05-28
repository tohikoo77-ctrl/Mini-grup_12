import uuid
from decimal import Decimal, ROUND_HALF_UP

from django.db import models
from django.conf import settings
from product.models import Product

MONEY_QUANT = Decimal("0.01")


def money(value):
    return Decimal(value or 0).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Cart-{self.user}"

    def get_total_quantity(self):
        return self.items.aggregate(total=models.Sum("quantity"))["total"] or 0

    def get_items_count(self):
        return self.items.count()

    def get_subtotal(self):
        total = self.items.aggregate(total=models.Sum("total_price"))["total"]
        return money(total)

    def get_total_price(self):
        return self.get_subtotal()


class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(default=1)
    price_snapshot = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("cart", "product")

    @property
    def line_total(self):
        return money(self.price_snapshot * self.quantity)

    def recalculate_totals(self):
        if self.price_snapshot is None:
            self.price_snapshot = self.product.price

        self.price_snapshot = money(self.price_snapshot)
        self.total_price = self.line_total

    def save(self, *args, **kwargs):
        self.recalculate_totals()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
