"""Serializery dla API sal."""

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from rooms.models import Room


class RoomListSerializer(serializers.ModelSerializer):
    equipment = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ("id", "name", "capacity", "location", "equipment", "created_at", "updated_at")

    @extend_schema_field(
        {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"name": {"type": "string"}, "qty": {"type": "integer"}},
            },
        }
    )
    def get_equipment(self, obj):
        return [{"name": re.equipment.name, "qty": re.qty} for re in obj.roomequipment_set.all()]


class RoomDetailSerializer(serializers.ModelSerializer):
    equipment = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ("id", "name", "capacity", "location", "equipment", "created_at", "updated_at")

    @extend_schema_field(
        {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"name": {"type": "string"}, "qty": {"type": "integer"}},
            },
        }
    )
    def get_equipment(self, obj):
        return [{"name": re.equipment.name, "qty": re.qty} for re in obj.roomequipment_set.all()]


class RoomCreateUpdateSerializer(serializers.ModelSerializer):
    """Do POST (create) i PATCH (update) – walidacja pól edytowalnych."""

    class Meta:
        model = Room
        fields = ("name", "capacity", "location")
