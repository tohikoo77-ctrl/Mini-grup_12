from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Order


class OrderCheckoutContractTests(APITestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            phone_number="+998901234567",
            password="testpass123",
            is_active=True,
            is_verified=True,
        )
        self.other_user = self.user_model.objects.create_user(
            phone_number="+998901234568",
            password="testpass123",
            is_active=True,
            is_verified=True,
        )
        self.order = Order.objects.create(
            user=self.user,
            phone="+998901234567",
            shipping_address_snapshot={"address_line": "Toshkent"},
        )
        self.other_order = Order.objects.create(
            user=self.other_user,
            phone="+998901234568",
            shipping_address_snapshot={"address_line": "Samarqand"},
        )
        self.client.force_authenticate(user=self.user)

    def test_checkout_requires_order_id(self):
        response = self.client.post(
            reverse("order-create"),
            data={},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("checkout_id", response.data)

    def test_checkout_accepts_only_order_id(self):
        response = self.client.post(
            reverse("order-create"),
            data={"checkout_id": str(self.order.id)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["order"]["id"], str(self.order.id))
        self.assertEqual(response.data["message"], "Order created")

    def test_checkout_rejects_foreign_order_id(self):
        response = self.client.post(
            reverse("order-create"),
            data={"order_id": str(self.other_order.id)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("checkout_id", response.data)
