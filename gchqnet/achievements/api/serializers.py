from rest_framework import serializers


class AchievementSubmissionSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    token = serializers.CharField()
