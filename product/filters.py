from django.db.models import Q


class ProductFilter:
    def __init__(self, queryset, params):
        self.queryset = queryset
        self.params = params

    def filter(self):
        qs = self.queryset

        qs = self._search(qs)
        qs = self._category(qs)
        qs = self._seller(qs)
        qs = self._price(qs)
        qs = self._availability(qs)

        return qs

    def _search(self, qs):
        search = self.params.get("search")
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        return qs

    def _category(self, qs):
        category = self.params.get("category")
        if category:
            qs = qs.filter(category_id=category)
        return qs

    def _seller(self, qs):
        seller = self.params.get("seller")
        if seller:
            qs = qs.filter(seller_id=seller)
        return qs

    def _price(self, qs):
        min_price = self.params.get("min_price")
        max_price = self.params.get("max_price")

        if min_price:
            try:
                qs = qs.filter(price__gte=float(min_price))
            except ValueError:
                pass

        if max_price:
            try:
                qs = qs.filter(price__lte=float(max_price))
            except ValueError:
                pass

        return qs

    def _availability(self, qs):
        is_available = self.params.get("is_available")

        if is_available is None:
            return qs

        if isinstance(is_available, str):
            is_available = is_available.lower() in ["true", "1", "yes"]

        return qs.filter(is_available=is_available)
    