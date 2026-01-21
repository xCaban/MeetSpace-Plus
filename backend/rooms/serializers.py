"""Serializery dla API sal."""

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from rooms.models import Equipment, Room, RoomEquipment


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
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "qty": {"type": "integer"},
                },
            },
        }
    )
    def get_equipment(self, obj):
        return [
            {"id": re.equipment.id, "name": re.equipment.name, "qty": re.qty}
            for re in obj.roomequipment_set.all()
        ]


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
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "qty": {"type": "integer"},
                },
            },
        }
    )
    def get_equipment(self, obj):
        return [
            {"id": re.equipment.id, "name": re.equipment.name, "qty": re.qty}
            for re in obj.roomequipment_set.all()
        ]


class RoomEquipmentInputSerializer(serializers.Serializer):
    """Serializer dla pojedynczego elementu sprzętu przypisywanego do sali."""

    equipment_id = serializers.IntegerField()
    qty = serializers.IntegerField(min_value=1, default=1)


class RoomCreateUpdateSerializer(serializers.ModelSerializer):
    """Do POST (create) i PATCH (update) – walidacja pól edytowalnych."""

    equipment = RoomEquipmentInputSerializer(many=True, required=False, write_only=True)

    class Meta:
        model = Room
        fields = ("name", "capacity", "location", "equipment")

    def validate_equipment(self, value):
        """Walidacja sprzętu: istnienie i brak duplikatów."""
        if not value:
            return value

        equipment_ids = [item["equipment_id"] for item in value]

        # Sprawdzenie duplikatów
        if len(equipment_ids) != len(set(equipment_ids)):
            raise serializers.ValidationError("Duplikaty sprzętu nie są dozwolone.")

        # Sprawdzenie czy wszystkie equipment_id istnieją
        existing = set(Equipment.objects.filter(id__in=equipment_ids).values_list("id", flat=True))
        missing = set(equipment_ids) - existing
        if missing:
            raise serializers.ValidationError(f"Nie znaleziono sprzętu o ID: {missing}")

        return value

    def create(self, validated_data):
        equipment_data = validated_data.pop("equipment", [])
        room = super().create(validated_data)
        self._save_equipment(room, equipment_data)
        return room

    def update(self, instance, validated_data):
        equipment_data = validated_data.pop("equipment", None)
        room = super().update(instance, validated_data)
        if equipment_data is not None:
            self._save_equipment(room, equipment_data)
        return room

    def _save_equipment(self, room, equipment_data):
        """Zastąpienie sprzętu w sali."""
        room.roomequipment_set.all().delete()
        for item in equipment_data:
            RoomEquipment.objects.create(
                room=room,
                equipment_id=item["equipment_id"],
                qty=item.get("qty", 1),
            )


class EquipmentSerializer(serializers.ModelSerializer):
    """Serializer dla sprzętu."""

    class Meta:
        model = Equipment
        fields = ("id", "name", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")
