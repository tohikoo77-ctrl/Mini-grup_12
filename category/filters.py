from django.db.models import Q

from common.mixins import parse_uuid_pk


class CategoryFilter:
    def __init__(self, queryset, params):
        self.queryset = queryset
        self.params = params

    def filter(self):
        qs = self.queryset
        qs = self._search(qs)
        qs = self._id(qs)
        return qs

    def _search(self, qs):
        search = self.params.get("search")
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(slug__icontains=search)
            )
        return qs

    def _id(self, qs):
        category_id = parse_uuid_pk(self.params.get("id"))
        if category_id is not None:
            qs = qs.filter(pk=category_id)
        return qs
