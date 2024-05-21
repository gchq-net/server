from django.core.validators import RegexValidator
from rest_framework import serializers


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
