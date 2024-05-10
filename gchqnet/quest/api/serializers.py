from rest_framework import serializers

from gchqnet.accounts.models import User
from gchqnet.quest.models import Leaderboard


class ScoreboardEntrySerializer(serializers.ModelSerializer):
    rank = serializers.IntegerField()
    capture_count = serializers.IntegerField()
    current_score = serializers.IntegerField()

    class Meta:
        model = User
        fields = ["username", "display_name", "rank", "capture_count", "current_score"]


class LeaderboardSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()
    created_by = serializers.StringRelatedField()

    class Meta:
        model = Leaderboard
        fields = ["id", "display_name", "owner", "enable_invites", "created_at", "created_by", "updated_at"]


class LeaderboardWithScoresSerializer(LeaderboardSerializer):
    scores = ScoreboardEntrySerializer(many=True)

    class Meta:
        model = Leaderboard
        fields = ["id", "display_name", "owner", "enable_invites", "scores", "created_at", "created_by", "updated_at"]
