from django.conf import settings
from django.db import models


class Reservation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELED = "canceled", "Canceled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    room = models.ForeignKey(
        "rooms.Room",
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    hold_expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reservations"
        indexes = [
            models.Index(
                fields=["room", "start_at"],
                name="reservations_room_start_idx",
            ),
            models.Index(
                fields=["user", "start_at"],
                name="reservations_user_start_idx",
            ),
        ]
        # Brak nakładania się slotów (room_id, [start_at, end_at]) – egzekwowane
        # w warstwie serwisowej (409 przy kolizji). ExclusionConstraint wymaga
        # PostgreSQL; przy SQLite (dev) pozostawiamy walidację w serwisie.
