from django.db.models import Q

from common.mixins import parse_uuid_pk


class OrderFilter:
    def __init__(self, queryset, params):
        self.queryset = queryset
        self.params = params

    def filter(self):
        qs = self.queryset
        qs = self._search(qs)
        qs = self._id(qs)
        qs = self._status(qs)
        return qs

    def _search(self, qs):
        search = self.params.get("search")
        if not search:
            return qs

        search_q = Q(phone__icontains=search) | Q(status__icontains=search)
        order_id = parse_uuid_pk(search)
        if order_id is not None:
            search_q |= Q(pk=order_id)

        return qs.filter(search_q)

    def _id(self, qs):
        order_id = parse_uuid_pk(self.params.get("id"))
        if order_id is not None:
            qs = qs.filter(pk=order_id)
        return qs

    def _status(self, qs):
        status_value = self.params.get("status")
        if status_value:
            qs = qs.filter(status=status_value)
        return qs
