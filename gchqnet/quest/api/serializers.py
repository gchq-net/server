from rest_framework import serializers

from gchqnet.accounts.models import User
from gchqnet.quest.api.fields import LocationNameField
from gchqnet.quest.models import Leaderboard
from gchqnet.quest.models.location import Location


class LeaderboardLinkedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "display_name"]


class ScoreboardEntrySerializer(serializers.ModelSerializer):
    rank = serializers.IntegerField()
    capture_count = serializers.IntegerField()
    current_score = serializers.IntegerField()

    class Meta:
        model = User
        fields = ["username", "display_name", "rank", "capture_count", "current_score"]


class LeaderboardSerializer(serializers.ModelSerializer):
    owner = LeaderboardLinkedUserSerializer()
    created_by = LeaderboardLinkedUserSerializer()

    class Meta:
        model = Leaderboard
        fields = ["id", "display_name", "owner", "enable_invites", "created_at", "created_by", "updated_at"]


class LeaderboardWithScoresSerializer(LeaderboardSerializer):
    scores = ScoreboardEntrySerializer(many=True)

    class Meta:
        model = Leaderboard
        fields = ["id", "display_name", "owner", "enable_invites", "scores", "created_at", "created_by", "updated_at"]


class LocationFeaturePropertySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(default="GCHQ.NET Scoreboard (Easy)")


class LocationFeatureGeometrySerializer(serializers.Serializer):
    coordinates = serializers.ListSerializer(default=[-2.377, 52.039], child=serializers.FloatField())
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
