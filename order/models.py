import uuid
from django.db import models
from django.conf import settings
from product.models import Product


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Kutilmoqda"
        PROCESSING = "processing", "Jarayonda"
        SHIPPED = "shipped", "Yolda"
        DELIVERED = "delivered", "Yetkazib berildi"
        CANCELLED = "cancelled", "Bekor qilindi"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    phone = models.CharField(max_length=20)
    shipping_address_snapshot = models.JSONField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def update_total_price(self):
        self.total_price = sum(item.total_price for item in self.items.all())
        self.save(update_fields=["total_price"])

    def __str__(self):
        return f"Order {self.id}"


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")

    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="order_items"
    )

    quantity = models.PositiveIntegerField(default=1)

    price_snapshot = models.DecimalField(max_digits=10, decimal_places=2)

    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_price = self.price_snapshot * self.quantity
        super().save(*args, **kwargs)
        self.order.update_total_price()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
