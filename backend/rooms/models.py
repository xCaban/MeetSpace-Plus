from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField(default=10, help_text="Pojemność (liczba osób)")
    location = models.CharField(
        max_length=255, blank=True, default="", help_text="Lokalizacja, np. piętro, budynek"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "rooms"


class Equipment(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "equipment"


class RoomEquipment(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "room_equipment"
        constraints = [
            models.UniqueConstraint(
                fields=["room", "equipment"],
                name="room_equipment_room_equipment_uniq",
            ),
        ]
