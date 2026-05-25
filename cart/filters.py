"""Cart ro'yxati uchun ID filtri."""

from __future__ import annotations

from django.db.models import QuerySet


class CartFilter:
    """?id= query parametri bo'yicha savatni filtrlash."""

    def __init__(self, queryset: QuerySet, params: dict) -> None:
        self.queryset = queryset
        self.params = params

    def filter(self) -> QuerySet:
        qs = self.queryset
        cart_id = self.params.get("id")
        if cart_id:
            qs = qs.filter(pk=cart_id)
        return qs
