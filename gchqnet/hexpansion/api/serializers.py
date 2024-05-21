from rest_framework import serializers

from gchqnet.hexpansion.models import Hexpansion


class HexpansionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hexpansion
        read_only_fields = ["id"]
        fields = ["id", "human_identifier", "eeprom_serial_number", "serial_number", "hardware_revision"]
