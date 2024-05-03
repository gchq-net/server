from rest_framework import serializers

from gchqnet.accounts.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "display_name"]
        read_only_fields = ["username"]
