"""Order ro'yxati uchun qidiruv va ID filtrlari."""

from __future__ import annotations

from django.db.models import Q, QuerySet


class OrderFilter:
    """?search=, ?id= va ?status= query parametrlarini qo'llaydi."""

    def __init__(self, queryset: QuerySet, params: dict) -> None:
        self.queryset = queryset
        self.params = params

    def filter(self) -> QuerySet:
        qs = self.queryset
        qs = self._search(qs)
        qs = self._id(qs)
        qs = self._status(qs)
        return qs

    def _search(self, qs: QuerySet) -> QuerySet:
        search = self.params.get("search")
        if search:
            qs = qs.filter(
                Q(phone__icontains=search)
                | Q(status__icontains=search)
                | Q(id__icontains=search)
            )
        return qs

    def _id(self, qs: QuerySet) -> QuerySet:
        order_id = self.params.get("id")
        if order_id:
            qs = qs.filter(pk=order_id)
        return qs

    def _status(self, qs: QuerySet) -> QuerySet:
        status_value = self.params.get("status")
        if status_value:
            qs = qs.filter(status=status_value)
        return qs
