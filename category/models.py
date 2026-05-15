import uuid
from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError


class FieldType(models.TextChoices):
    TEXT = "text", "Text"
    NUMBER = "number", "Number"
    DROPDOWN = "dropdown", "Dropdown"
    CHECKBOX = "checkbox", "Checkbox"


class CategoryQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True, is_deleted=False)


class CategoryManager(models.Manager):
    def get_queryset(self):
        return CategoryQuerySet(self.model, using=self._db).active()


def generate_unique_slug(instance, base_slug):
    model = instance.__class__

    base_slug = base_slug or str(instance.id)
    slug = base_slug
    counter = 1

    while model.objects.filter(slug=slug).exclude(id=instance.id).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, db_index=True)

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children"
    )

    image = models.ImageField(upload_to="categories/%Y/%m/", null=True, blank=True)
    icon = models.CharField(max_length=50, null=True, blank=True)

    is_active = models.BooleanField(default=True, db_index=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    order = models.PositiveIntegerField(default=0, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CategoryManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ["order", "name"]

        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["parent"]),
            models.Index(fields=["is_active", "is_deleted"]),
            models.Index(fields=["parent", "order"]),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["parent", "name"],
                name="unique_category_per_parent"
            )
        ]

    def clean(self):
        if self.parent_id and self.parent_id == self.id:
            raise ValidationError("Category cannot be parent of itself")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, slugify(self.name))

        self.full_clean()
        super().save(*args, **kwargs)

    def get_full_path(self):
        names = []
        current = self

        while current:
            names.append(current.name)
            current = current.parent

        return " > ".join(reversed(names))

    def __str__(self):
        return self.name


class CategoryProperty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="properties"
    )

    name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=20, choices=FieldType.choices)
    is_required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

        constraints = [
            models.UniqueConstraint(
                fields=["category", "name"],
                name="unique_category_property"
            )
        ]

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class PropertyOption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    property = models.ForeignKey(
        CategoryProperty,
        on_delete=models.CASCADE,
        related_name="options"
    )

    value = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["property", "value"],
                name="unique_property_option"
            )
        ]

    def __str__(self):
        return f"{self.property.name} - {self.value}"
    