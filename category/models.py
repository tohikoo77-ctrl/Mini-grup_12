import uuid
from django.db import models
from django.utils.text import slugify


class FieldType(models.TextChoices):
    TEXT = "text", "Text"
    NUMBER = "number", "Number"
    DROPDOWN = "dropdown", "Dropdown"
    CHECKBOX = "checkbox", "Checkbox"


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )

    image = models.ImageField(upload_to="categories/%Y/%m/", null=True, blank=True)
    icon = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Category.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CategoryProperty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="properties"
    )

    name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=20, choices=FieldType.choices)
    is_required = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    class Meta:
        verbose_name = "Category Property"
        verbose_name_plural = "Category Properties"
        ordering = ["order"]

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class PropertyOption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(
        CategoryProperty, on_delete=models.CASCADE, related_name="options"
    )
    value = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Property Option"
        verbose_name_plural = "Property Options"

    def __str__(self):
        return f"{self.property.name}: {self.value}"
