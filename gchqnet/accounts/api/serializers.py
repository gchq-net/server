from rest_framework import serializers

from gchqnet.accounts.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "display_name"]
        read_only_fields = ["username"]


class UserTokenRequestSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    otp = serializers.CharField(max_length=6, min_length=6)


class UserTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["api_token"]
