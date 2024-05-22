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


class BadgeCaptureProofSerializer(serializers.Serializer):
    sn = serializers.IntegerField(min_value=0, max_value=2**72, label="Serial Number")
    rand = serializers.IntegerField(min_value=0, max_value=2**128, label="Cryptographic Nonce")
    hmac = serializers.CharField(
        label="SHA256 HMAC",
        help_text="formatted as hexdigest",
        max_length=64,
        min_length=64,
        validators=[RegexValidator("^[0-9a-f]{64}$", "The HMAC does not appear to be in the correct format.")],
    )


class BadgeCaptureWiFiStatsSerializer(serializers.Serializer):
    bssid = serializers.CharField(
        max_length=17,
        min_length=17,
        validators=[
            RegexValidator(
                "^([0-9A-F]{2}[-]){5}([0-9A-F]{2})$", "The BSSID does not appear to be in the correct format."
            )
        ],
    )
    channel = serializers.IntegerField(min_value=1, max_value=200)
    rssi = serializers.IntegerField(min_value=-200, max_value=200)


class BadgeCaptureSubmissionSerializer(BadgeAPIRequestSerializer):
    capture = BadgeCaptureProofSerializer()
    app_rev = serializers.CharField(max_length=20)
    fw_rev = serializers.CharField(max_length=20)
    wifi = BadgeCaptureWiFiStatsSerializer()


class BadgeCaptureSuccessSerializer(serializers.Serializer):
    result = serializers.CharField(default="success")
    repeat = serializers.BooleanField()
    location_name = serializers.CharField(max_length=30)
    difficulty = serializers.CharField()


class BadgeCaptureFailureSerializer(serializers.Serializer):
    result = serializers.CharField(default="fail")
    message = serializers.CharField()
