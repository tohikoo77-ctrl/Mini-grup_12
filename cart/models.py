import uuid
from django.db import models
from django.conf import settings
from product.models import Product


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
<<<<<<< HEAD
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart"
=======
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart"
>>>>>>> 46fcb280bb59991e63e20580eaec33e113b5dd3e
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Cart-{self.user.phone_number}"

    def get_total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    def get_total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
<<<<<<< HEAD
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        "announcements.Announcement",
        on_delete=models.PROTECT,
        related_name="cart_items",
    )
=======

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="cart_items"
    )

>>>>>>> 46fcb280bb59991e63e20580eaec33e113b5dd3e
    quantity = models.PositiveIntegerField(default=1)

    price_snapshot = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("cart", "product")

    def save(self, *args, **kwargs):
        if not self.price_snapshot:
            self.price_snapshot = self.product.price

        self.total_price = self.price_snapshot * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
<<<<<<< HEAD
        return f"{self.product.name}x{self.quantity}"
=======
        return f"{self.product.name} x {self.quantity}"
>>>>>>> 46fcb280bb59991e63e20580eaec33e113b5dd3e
