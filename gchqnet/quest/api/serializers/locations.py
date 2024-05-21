from rest_framework import serializers

from gchqnet.quest.api.fields import LocationNameField
from gchqnet.quest.models.location import Location


class LocationFeaturePropertySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(default="GCHQ.NET Scoreboard (Easy)")
    colour = serializers.CharField()
    difficulty = serializers.CharField()


class LocationFeatureGeometrySerializer(serializers.Serializer):
    coordinates = serializers.ListSerializer(
        default=[-2.383657, 52.032173], child=serializers.DecimalField(max_digits=16, decimal_places=13)
    )
    type = serializers.CharField(default="Point")


class LocationFeatureSerializer(serializers.Serializer):
    type = serializers.CharField(default="Feature")
    properties = LocationFeaturePropertySerializer()
    geometry = LocationFeatureGeometrySerializer()
    id = serializers.IntegerField()


class LocationGeoJSONSerializer(serializers.Serializer):
    type = serializers.CharField(default="FeatureCollection")
    features = LocationFeatureSerializer(many=True)


class LocationSerializer(serializers.ModelSerializer):
    display_name = LocationNameField(source="*")
    found_at = serializers.DateTimeField()

    class Meta:
        model = Location
        fields = ["id", "display_name", "hint", "difficulty", "found_at"]
