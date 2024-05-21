from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from gchqnet.quest.models.location import Location


@extend_schema_field(str)
class LocationNameField(serializers.Field):
    def to_representation(self, value: Location) -> str:
        if value.found_at is not None:  # type: ignore[attr-defined]
            return value.display_name
        else:
            return "???"
