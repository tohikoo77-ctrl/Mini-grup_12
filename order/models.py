import uuid
from decimal import Decimal, ROUND_HALF_UP

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from product.models import Product

MONEY_QUANT = Decimal("0.01")


def money(value):
    return Decimal(value or 0).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["active", "valid_from", "valid_to"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    discount_percent__gte=1,
                    discount_percent__lte=100,
                ),
                name="promo_discount_percent_1_100",
            )
        ]

    def is_valid(self):
        now = timezone.now()
        return (
            self.active
            and self.valid_from <= now <= self.valid_to
            and 1 <= self.discount_percent <= 100
        )

    def __str__(self):
        return self.code


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="orders",
    )
    promocode = models.ForeignKey(
        PromoCode,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    phone = models.CharField(max_length=20)
    shipping_address_snapshot = models.JSONField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["created_at"]),
        ]

    def can_be_modified(self):
        return self.status in {self.Status.PENDING, self.Status.PROCESSING}

    def can_be_cancelled(self):
        return self.status not in {
            self.Status.SHIPPED,
            self.Status.DELIVERED,
            self.Status.CANCELLED,
        }

    def get_items_count(self):
        return self.items.count()

    def get_total_quantity(self):
        return self.items.aggregate(total=models.Sum("quantity"))["total"] or 0

    def get_subtotal(self):
        total = self.items.aggregate(total=models.Sum("total_price"))["total"]
        return money(total)

    def get_discount_percent(self):
        if self.promocode and self.promocode.is_valid():
            return self.promocode.discount_percent
        return 0

    def get_discount_amount(self):
        subtotal = self.get_subtotal()
        percent = self.get_discount_percent()

        if not percent:
            return money(0)

        discount = money(subtotal * Decimal(percent) / Decimal("100"))
        return min(discount, subtotal)

    def calculate_total_price(self):
        total = self.get_subtotal() - self.get_discount_amount()
        return max(money(total), money(0))

    def update_total_price(self):
        self.total_price = self.calculate_total_price()
        self.save(update_fields=["total_price", "updated_at"])
        return self.total_price

    def __str__(self):
        return f"Order-{self.id}"


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    quantity = models.PositiveIntegerField(default=1)
    price_snapshot = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def line_total(self):
        return money(self.price_snapshot * self.quantity)

    def recalculate_totals(self):
        if self.price_snapshot is None:
            self.price_snapshot = self.product.price

        self.price_snapshot = money(self.price_snapshot)
        self.total_price = self.line_total

    def save(self, *args, update_order_total=True, **kwargs):
        self.recalculate_totals()
        super().save(*args, **kwargs)

        if update_order_total and self.order_id:
            self.order.update_total_price()

    def delete(self, *args, update_order_total=True, **kwargs):
        order = self.order
        result = super().delete(*args, **kwargs)

        if update_order_total:
            order.update_total_price()

        return result

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
