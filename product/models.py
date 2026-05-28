import uuid
<<<<<<< HEAD
from decimal import Decimal

=======

from django.db import models
from django.utils.text import slugify
>>>>>>> 1ad953692057d6f3a9567c6264443e1c3567615c
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, transaction
from django.db.models import Q
from django.db.models import F
from django.utils.text import slugify

from category.models import Category


class ActiveProductManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(is_deleted=False, is_active=True)
        )


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
<<<<<<< HEAD

    name = models.CharField(max_length=200, db_index=True)
=======
    name = models.CharField(max_length=200)
>>>>>>> 1ad953692057d6f3a9567c6264443e1c3567615c
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    description = models.TextField(blank=True, null=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        db_index=True,
    )

    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )

    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        editable=False,
    )

    stock = models.PositiveIntegerField(default=0)

    is_available = models.BooleanField(default=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        db_index=True,
    )

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="products",
        db_index=True,
    )

    rating = models.FloatField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )

    views = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ActiveProductManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ("-created_at",)

        indexes = [
            models.Index(fields=["price"]),
            models.Index(fields=["category"]),
            models.Index(fields=["seller"]),
            models.Index(fields=["is_active", "is_deleted"]),
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["seller", "is_active"]),
            models.Index(fields=["price", "is_active"]),
        ]

        constraints = [
            models.CheckConstraint(
                check=Q(price__gte=0),
                name="product_price_gte_0",
            ),
            models.CheckConstraint(
                check=Q(old_price__gte=0) | Q(old_price__isnull=True),
                name="product_old_price_gte_0",
            ),
            models.CheckConstraint(
                check=Q(rating__gte=0) & Q(rating__lte=5),
                name="product_rating_range",
            ),
        ]

    def generate_slug(self):
        base_slug = slugify(self.name) or "product"
        slug = base_slug
        counter = 1

        qs = Product.all_objects.exclude(id=self.id)

        while qs.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    def calculate_discount(self):
        if self.old_price and self.old_price > self.price:
            return self.old_price - self.price
        return None

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_slug()

        self.discount_price = self.calculate_discount()

        super().save(*args, **kwargs)

    def soft_delete(self):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])

    def restore(self):
        self.is_deleted = False
        self.is_active = True
        self.save(update_fields=["is_deleted", "is_active"])

<<<<<<< HEAD
    def increase_views(self):
        Product.all_objects.filter(id=self.id).update(
            views=F("views") + 1
        )

    def __str__(self):
        return f"{self.name} | {self.price}"
=======
class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/%Y/%m/")
    is_main = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_main", "-created_at"]
        indexes = [models.Index(fields=["product"])]

    def save(self, *args, **kwargs):
        if self.is_main:
            ProductImage.objects.filter(
                product=self.product,
                is_main=True
            ).exclude(id=self.id).update(is_main=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} image"


class Favourite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favourites")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="favourited_by")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "product"], name="unique_favourite")
        ]
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self):
        return f"{self.user} -> {self.product}"
>>>>>>> 1ad953692057d6f3a9567c6264443e1c3567615c
    