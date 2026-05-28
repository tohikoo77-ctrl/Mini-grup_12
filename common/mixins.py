"""Umumiy DRF mixinlari: UUID primary key."""

from __future__ import annotations

import uuid
from typing import Any

from rest_framework.exceptions import NotFound

ID_NOT_FOUND_MESSAGE = "Объект с указанным идентификатором не найден."


def parse_uuid_pk(raw_value: Any) -> uuid.UUID | None:
    """Query param yoki URL dan UUID pk ni parse qiladi."""
    if raw_value is None or raw_value == "":
        return None
    try:
        return uuid.UUID(str(raw_value))
    except (TypeError, ValueError, AttributeError):
        return None


class UUIDLookupMixin:
    """ViewSet uchun UUID primary key bilan obyekt qidirish."""

    lookup_field = "pk"
    lookup_url_kwarg: str | None = None

    def get_object(self) -> Any:
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        raw_pk = self.kwargs.get(lookup_url_kwarg)

        pk = parse_uuid_pk(raw_pk)
        if pk is None:
            raise NotFound(detail=ID_NOT_FOUND_MESSAGE)

        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.filter(pk=pk).first()

        if obj is None:
            raise NotFound(detail=ID_NOT_FOUND_MESSAGE)

        self.check_object_permissions(self.request, obj)
        return obj
