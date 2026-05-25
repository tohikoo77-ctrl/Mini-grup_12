"""Category ro'yxati uchun qidiruv va ID filtrlari."""

from __future__ import annotations

from django.db.models import Q, QuerySet


class CategoryFilter:
    """?search= va ?id= query parametrlarini qo'llaydi."""

    def __init__(self, queryset: QuerySet, params: dict) -> None:
        self.queryset = queryset
        self.params = params

    def filter(self) -> QuerySet:
        qs = self.queryset
        qs = self._search(qs)
        qs = self._id(qs)
        return qs

    def _search(self, qs: QuerySet) -> QuerySet:
        search = self.params.get("search")
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(slug__icontains=search)
            )
        return qs

    def _id(self, qs: QuerySet) -> QuerySet:
        category_id = self.params.get("id")
        if category_id:
            qs = qs.filter(pk=category_id)
        return qs
