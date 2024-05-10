from rest_framework import serializers

from gchqnet.accounts.models import User


class ScoreboardEntrySerializer(serializers.ModelSerializer):
    rank = serializers.IntegerField()
    capture_count = serializers.IntegerField()
    current_score = serializers.IntegerField()

    class Meta:
        model = User
        fields = ["username", "display_name", "rank", "capture_count", "current_score"]
