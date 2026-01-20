"""Serializery dla API rezerwacji."""

from rest_framework import serializers

from reservations.models import Reservation
from rooms.models import Room


class ReservationListSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source="room.name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Reservation
        fields = (
            "id",
            "user",
            "user_email",
            "room",
            "room_name",
            "status",
            "start_at",
            "end_at",
            "hold_expires_at",
            "created_at",
            "updated_at",
        )


class ReservationDetailSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source="room.name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Reservation
        fields = (
            "id",
            "user",
            "user_email",
            "room",
            "room_name",
            "status",
            "start_at",
            "end_at",
            "hold_expires_at",
            "created_at",
            "updated_at",
        )


class ReservationCreateSerializer(serializers.Serializer):
    room_id = serializers.IntegerField()
    start_at = serializers.DateTimeField()
    end_at = serializers.DateTimeField()

    def validate(self, data):
        if data["start_at"] >= data["end_at"]:
            raise serializers.ValidationError({"end_at": "end_at musi być później niż start_at"})
        if not Room.objects.filter(pk=data["room_id"]).exists():
            raise serializers.ValidationError({"room_id": "Sala o podanym id nie istnieje"})
        return data
