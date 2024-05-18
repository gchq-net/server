from typing import Any

from django.core.validators import RegexValidator
from rest_framework import serializers

from gchqnet.accounts.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    current_score = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ["username", "display_name", "current_score"]
        read_only_fields = ["username"]

    def get_current_score(self, user: User) -> int:
        return user.get_current_score()


class UserTokenRequestSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    otp = serializers.CharField(max_length=6, min_length=6, required=False)
    password = serializers.CharField(required=False)

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        if not (bool(data.get("otp")) ^ bool(data.get("password"))):
            raise serializers.ValidationError("You must provide one of a password or OTP.")
        return super().validate(data)


class UserTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["api_token"]


class BadgeAPIRequestSerializer(serializers.Serializer):
    mac_address = serializers.CharField(
        max_length=17,
        min_length=17,
        validators=[
            RegexValidator(
                "^([0-9A-F]{2}[-]){5}([0-9A-F]{2})$", "The MAC address does not appear to be in the correct format."
            )
        ],
    )
    badge_secret = serializers.CharField(
        max_length=64,
        min_length=64,
        validators=[RegexValidator("^[0-9a-f]{64}$", "The badge secret does not appear to be in the correct format.")],
    )


class BadgeOTPResponseSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    otp = serializers.CharField(min_length=6, max_length=6)
