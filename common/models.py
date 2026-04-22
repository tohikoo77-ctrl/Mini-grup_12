import uuid
from django.db import models
from django.conf import settings


class Region(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class District(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, related_name="districts"
    )
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["region", "order", "name"]
        unique_together = ("region", "name")

    def __str__(self):
        return f"{self.region.name} - {self.name}"


class UserAddress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="addresses"
    )
    region = models.ForeignKey(
        Region, on_delete=models.PROTECT, related_name="addresses"
    )
    district = models.ForeignKey(
        District, on_delete=models.PROTECT, related_name="addresses"
    )
    address_line = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.phone_number} - {self.address_line}"
