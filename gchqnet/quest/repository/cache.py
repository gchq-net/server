from django.core.cache import cache
from queryish import Queryish

from gchqnet.accounts.models.user import UserQuerySet


class CachedScoreboardQuerySet(Queryish):
    def __init__(self, qs: UserQuerySet, name: str) -> None:
        super().__init__()
        self._qs = qs
        self.filter_fields = ["display_name__ilike"]
        self.ordering = ("rank", "capture_count", "display_name")
        self.ordering_fields = ("rank", "capture_count", "current_score", "display_name")
        self._cache_key = f"gchqnet__scoreboard__{name}__data"

    def run_query(self) -> list[dict]:
        if not (data := cache.get(self._cache_key)):
            # Evaluate qs
            data = list(self._qs.values("id", "username", "display_name", "rank", "capture_count", "current_score"))
            cache.set(self._cache_key, data)

        # Filter the data by display name
        filter_dict = dict(self.filters)
        if "display_name__ilike" in filter_dict.keys():
            data = [
                entry for entry in data if filter_dict["display_name__ilike"].lower() in entry["display_name"].lower()
            ]

        # Sort the list by `self.ordering` - a tuple of field names
        data.sort(key=lambda c: [c.get(field, None) for field in self.ordering])

        return data
