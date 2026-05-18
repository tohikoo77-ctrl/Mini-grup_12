import uuid
from django.db import models
from django.utils.text import slugify


class FieldType(models.TextChoices):
    TEXT = "text", "Text"
    NUMBER = "number", "Number"
    DROPDOWN = "dropdown", "Dropdown"
    CHECKBOX = "checkbox", "Checkbox"


def generate_unique_slug(instance, base_slug):
    slug = base_slug
    counter = 1
    model = instance.__class__

    while model.objects.filter(slug=slug).exclude(id=instance.id).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            is_active=True,
            is_deleted=False
        )


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children"
    )

    image = models.ImageField(upload_to="categories/%Y/%m/", null=True, blank=True)
    icon = models.CharField(max_length=50, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        ordering = ["order", "name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["name"]),
            models.Index(fields=["parent"]),
            models.Index(fields=["is_active", "is_deleted"]),
            models.Index(fields=["is_deleted", "is_active"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, slugify(self.name))
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
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order"]
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["field_type"]),
        ]
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