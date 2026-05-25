"""Umumiy DRF mixinlari: UUID bo'yicha qidiruv va 404 xabari."""

from __future__ import annotations

import uuid
from typing import Any

from rest_framework.exceptions import NotFound

# Barcha ID lookup endpointlari uchun yagona xabar
ID_NOT_FOUND_MESSAGE = "Объект с указанным идентификатором не найден."


class UUIDLookupMixin:
    """
    ViewSet/APIView uchun UUID primary key bilan obyekt qidirish.

    Noto'g'ri UUID yoki mavjud bo'lmagan ID uchun 404 qaytaradi.
    """

    lookup_field = "pk"
    lookup_url_kwarg: str | None = None

    def get_object(self) -> Any:
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        raw_pk = self.kwargs.get(lookup_url_kwarg)

        try:
            pk = uuid.UUID(str(raw_pk))
        except (TypeError, ValueError, AttributeError):
            raise NotFound(detail=ID_NOT_FOUND_MESSAGE)

        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.filter(pk=pk).first()

        if obj is None:
            raise NotFound(detail=ID_NOT_FOUND_MESSAGE)

        self.check_object_permissions(self.request, obj)
        return obj
