"""
Komenda seed: dane przykładowe (sale, equipment, userzy, role, rezerwacje).

Uruchomienie: docker compose exec backend python manage.py seed
              docker compose exec backend python manage.py seed --reset
"""

import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import Role, UserRole
from reservations.models import Reservation
from rooms.models import Equipment, Room, RoomEquipment

User = get_user_model()

SEED_PASSWORD = "seedhaslo1"

# 10 sal: (name, capacity, location)
ROOMS = [
    ("Sala A", 6, "Budynek A, parter"),
    ("Sala B", 8, "Budynek A, parter"),
    ("Sala C", 4, "Budynek A, I piętro"),
    ("Sala konferencyjna 1", 20, "Budynek B, II piętro"),
    ("Sala konferencyjna 2", 16, "Budynek B, II piętro"),
    ("Pokój 101", 4, "Budynek A, I piętro"),
    ("Pokój 102", 4, "Budynek A, I piętro"),
    ("Sala spotkań", 10, "Budynek B, parter"),
    ("Sala szkoleniowa", 24, "Budynek B, I piętro"),
    ("Cabinet", 2, "Budynek A, parter"),
]

# 5 equipment
EQUIPMENT_NAMES = ["Projektor", "Tablica suchościeralna", "Telekonferencja", "Klimatyzacja", "Whiteboard"]

# 10 użytkowników (pierwszych 2 = admin)
USER_EMAILS = [
    "admin1@example.com",
    "admin2@example.com",
    "anna.kowalska@example.com",
    "jan.nowak@example.com",
    "maria.wisniewska@example.com",
    "piotr.lewandowski@example.com",
    "katarzyna.dabrowska@example.com",
    "tomasz.kaminska@example.com",
    "agnieszka.wójcik@example.com",
    "michal.kowalczyk@example.com",
]

# 20 par (room_index 0..9, equipment_index 0..4) – room_equipment
ROOM_EQUIPMENT_PAIRS = [
    (0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 3), (2, 0), (2, 1), (3, 0), (3, 1),
    (3, 2), (3, 3), (4, 0), (4, 2), (4, 3), (5, 0), (5, 4), (6, 0), (6, 4), (7, 0),
]


class Command(BaseCommand):
    help = "Tworzy dane przykładowe: 10 sal, 5 equipment, 20 room_equipment, 10 userów (2 admin), 20–30 rezerwacji. --reset: czyści i odtwarza."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Usuwa dane seedowe (Reservation, UserRole, RoomEquipment, Room, Equipment) i odtwarza od zera.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        reset = options["reset"]
        tz = timezone.get_current_timezone()
        now = timezone.localtime(timezone.now(), tz)

        if reset:
            self._delete_seed_data()
            self.stdout.write("Usunięto dane seedowe.")

        # Role
        role_admin, _ = Role.objects.get_or_create(name="admin")
        role_user, _ = Role.objects.get_or_create(name="user")

        # 10 userów (2 admin), user_roles
        users = []
        for i, email in enumerate(USER_EMAILS):
            u, created = User.objects.get_or_create(
                username=email,
                defaults={"email": email, "is_staff": i < 2, "is_active": True},
            )
            if created:
                u.set_password(SEED_PASSWORD)
                u.save(update_fields=["password"])
            users.append(u)
            UserRole.objects.get_or_create(user=u, role=role_admin if i < 2 else role_user)
        self.stdout.write(self.style.SUCCESS(f"Userzy: {len(users)} (2 admin), hasło: {SEED_PASSWORD}"))

        # 10 sal
        rooms = []
        for name, cap, loc in ROOMS:
            r, _ = Room.objects.get_or_create(
                name=name,
                defaults={"capacity": cap, "location": loc},
            )
            r.capacity = cap
            r.location = loc
            r.save(update_fields=["capacity", "location"])
            rooms.append(r)
        self.stdout.write(self.style.SUCCESS(f"Sale: {len(rooms)}"))

        # 5 equipment
        equipments = []
        for n in EQUIPMENT_NAMES:
            e, _ = Equipment.objects.get_or_create(name=n)
            equipments.append(e)
        self.stdout.write(self.style.SUCCESS(f"Equipment: {len(equipments)}"))

        # 20 room_equipment
        for ri, ei in ROOM_EQUIPMENT_PAIRS:
            RoomEquipment.objects.get_or_create(
                room=rooms[ri],
                equipment=equipments[ei],
                defaults={"qty": 1 if ei != 3 else 2},
            )
        self.stdout.write(self.style.SUCCESS("RoomEquipment: 20"))

        # 20–30 rezerwacji (tylko gdy brak lub --reset)
        if reset or Reservation.objects.count() == 0:
            base = now.replace(hour=0, minute=0, second=0, microsecond=0)
            statuses = (
                [Reservation.Status.PENDING] * 6
                + [Reservation.Status.CONFIRMED] * 14
                + [Reservation.Status.CANCELED] * 6
            )
            random.shuffle(statuses)
            created = 0
            for i in range(min(26, len(statuses))):
                room = rooms[i % len(rooms)]
                day_off = (i // len(rooms)) % 14
                hour = 8 + (i % 10)
                if hour >= 18:
                    hour = 8 + (i % 8)
                start = base + timedelta(days=day_off, hours=hour)
                end = start + timedelta(hours=1)
                user = random.choice(users)
                st = statuses[i]
                hold = None
                if st == Reservation.Status.PENDING:
                    hold = now + timedelta(minutes=random.randint(5, 14))
                Reservation.objects.create(
                    user=user,
                    room=room,
                    status=st,
                    start_at=start,
                    end_at=end,
                    hold_expires_at=hold,
                )
                created += 1
            self.stdout.write(self.style.SUCCESS(f"Rezerwacje: {created} (kilka pending z hold_expires_at w przyszłości)"))
        else:
            self.stdout.write("Rezerwacje: pominięto (istnieją; użyj --reset aby odtworzyć).")

        self.stdout.write(self.style.SUCCESS("Seed zakończony."))

    def _delete_seed_data(self):
        Reservation.objects.all().delete()
        UserRole.objects.all().delete()
        RoomEquipment.objects.all().delete()
        Room.objects.all().delete()
        Equipment.objects.all().delete()
