"""Testy integracyjne API rezerwacji: list, create, confirm, cancel."""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Role, User, UserRole
from reservations.models import Reservation
from rooms.models import Room


def _dt(year, month, day, h, m, tz=None):
    if tz is None:
        tz = timezone.get_current_timezone()
    return timezone.make_aware(datetime(year, month, day, h, m), tz)


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def role_user(db):
    return Role.objects.get_or_create(name="user")[0]


@pytest.fixture
def role_admin(db):
    return Role.objects.get_or_create(name="admin")[0]


@pytest.fixture
def user(db, role_user):
    u = User.objects.create_user(username="u1@ex.com", password="test", email="u1@ex.com")
    UserRole.objects.get_or_create(user=u, role=role_user)
    return u


@pytest.fixture
def admin_user(db, role_admin):
    u = User.objects.create_user(
        username="admin@ex.com", password="test", email="admin@ex.com", is_staff=True
    )
    UserRole.objects.get_or_create(user=u, role=role_admin)
    return u


@pytest.fixture
def room(db):
    return Room.objects.create(name="Sala A", capacity=6, location="Parter")


@pytest.fixture
def reservation(user, room):
    return Reservation.objects.create(
        user=user,
        room=room,
        status=Reservation.Status.PENDING,
        start_at=_dt(2025, 2, 10, 10, 0),
        end_at=_dt(2025, 2, 10, 11, 0),
    )


@pytest.mark.django_db
class TestReservationsListAPI:
    def test_unauthenticated_401(self, client):
        r = client.get("/api/reservations/")
        assert r.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_200_empty(self, client, user):
        client.force_authenticate(user=user)
        r = client.get("/api/reservations/")
        assert r.status_code == status.HTTP_200_OK
        assert r.json() == []

    def test_authenticated_200_with_data(self, client, user, reservation):
        client.force_authenticate(user=user)
        r = client.get("/api/reservations/")
        assert r.status_code == status.HTTP_200_OK
        data = r.json()
        assert len(data) == 1
        assert data[0]["id"] == reservation.id
        assert data[0]["status"] == "pending"
        assert "room_name" in data[0]

    def test_filter_room_id(self, client, user, room, reservation):
        room2 = Room.objects.create(name="Sala B", capacity=4, location="I piętro")
        Reservation.objects.create(
            user=user,
            room=room2,
            status=Reservation.Status.CONFIRMED,
            start_at=_dt(2025, 2, 11, 9, 0),
            end_at=_dt(2025, 2, 11, 10, 0),
        )
        client.force_authenticate(user=user)
        r = client.get("/api/reservations/", {"room_id": room.id})
        assert r.status_code == status.HTTP_200_OK
        assert len(r.json()) == 1
        assert r.json()[0]["room"] == room.id

    def test_filter_status(self, client, user, reservation):
        reservation.status = Reservation.Status.CONFIRMED
        reservation.save(update_fields=["status"])
        client.force_authenticate(user=user)
        r = client.get("/api/reservations/", {"status": "confirmed"})
        assert r.status_code == status.HTTP_200_OK
        assert len(r.json()) == 1
        assert r.json()[0]["status"] == "confirmed"


@pytest.mark.django_db
@patch("reservations.services.booking.expire_hold")
class TestReservationsCreateAPI:
    def test_unauthenticated_401(self, mock_expire, client, room):
        r = client.post(
            "/api/reservations/",
            {
                "room_id": room.id,
                "start_at": "2025-02-15T10:00:00+01:00",
                "end_at": "2025-02-15T11:00:00+01:00",
            },
            format="json",
        )
        assert r.status_code == status.HTTP_401_UNAUTHORIZED
        mock_expire.apply_async.assert_not_called()

    def test_validation_400(self, mock_expire, client, user, room):
        client.force_authenticate(user=user)
        r = client.post(
            "/api/reservations/",
            {
                "room_id": room.id,
                "start_at": "2025-02-15T11:00:00+01:00",
                "end_at": "2025-02-15T10:00:00+01:00",
            },
            format="json",
        )
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        mock_expire.apply_async.assert_not_called()

    def test_created_201(self, mock_expire, client, user, room):
        client.force_authenticate(user=user)
        r = client.post(
            "/api/reservations/",
            {
                "room_id": room.id,
                "start_at": "2025-02-15T10:00:00+01:00",
                "end_at": "2025-02-15T11:00:00+01:00",
            },
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED
        data = r.json()
        assert data["status"] == "pending"
        assert data["room"] == room.id
        assert "hold_expires_at" in data
        mock_expire.apply_async.assert_called_once()

    def test_collision_409(self, mock_expire, client, user, room):
        Reservation.objects.create(
            user=user,
            room=room,
            status=Reservation.Status.CONFIRMED,
            start_at=_dt(2025, 2, 15, 10, 0),
            end_at=_dt(2025, 2, 15, 11, 0),
        )
        client.force_authenticate(user=user)
        r = client.post(
            "/api/reservations/",
            {
                "room_id": room.id,
                "start_at": "2025-02-15T10:00:00+01:00",
                "end_at": "2025-02-15T11:00:00+01:00",
            },
            format="json",
        )
        assert r.status_code == status.HTTP_409_CONFLICT
        assert "kolizja" in r.json().get("detail", "").lower()
        mock_expire.apply_async.assert_not_called()


@pytest.mark.django_db
@patch("reservations.services.booking.send_notifications")
class TestReservationsConfirmAPI:
    def test_owner_200(self, mock_send, client, user, reservation):
        client.force_authenticate(user=user)
        r = client.post(f"/api/reservations/{reservation.id}/confirm/")
        assert r.status_code == status.HTTP_200_OK
        assert r.json()["status"] == "confirmed"
        reservation.refresh_from_db()
        assert reservation.status == Reservation.Status.CONFIRMED
        mock_send.delay.assert_called_once_with(reservation.id, "confirmed")

    def test_admin_200(self, mock_send, client, admin_user, user, room):
        res = Reservation.objects.create(
            user=user,
            room=room,
            status=Reservation.Status.PENDING,
            start_at=_dt(2025, 2, 10, 14, 0),
            end_at=_dt(2025, 2, 10, 15, 0),
        )
        client.force_authenticate(user=admin_user)
        r = client.post(f"/api/reservations/{res.id}/confirm/")
        assert r.status_code == status.HTTP_200_OK
        assert r.json()["status"] == "confirmed"

    def test_non_owner_403(self, mock_send, client, user, room, role_user):
        other = User.objects.create_user(
            username="other@ex.com", password="x", email="other@ex.com"
        )
        UserRole.objects.get_or_create(user=other, role=role_user)
        res = Reservation.objects.create(
            user=user,
            room=room,
            status=Reservation.Status.PENDING,
            start_at=_dt(2025, 2, 10, 14, 0),
            end_at=_dt(2025, 2, 10, 15, 0),
        )
        client.force_authenticate(user=other)
        r = client.post(f"/api/reservations/{res.id}/confirm/")
        assert r.status_code == status.HTTP_403_FORBIDDEN
        mock_send.delay.assert_not_called()

    def test_not_pending_400(self, mock_send, client, user, reservation):
        reservation.status = Reservation.Status.CONFIRMED
        reservation.save(update_fields=["status"])
        client.force_authenticate(user=user)
        r = client.post(f"/api/reservations/{reservation.id}/confirm/")
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        mock_send.delay.assert_not_called()


@pytest.mark.django_db
@patch("reservations.services.booking.send_notifications")
class TestReservationsCancelAPI:
    def test_owner_200(self, mock_send, client, user, reservation):
        client.force_authenticate(user=user)
        r = client.post(f"/api/reservations/{reservation.id}/cancel/")
        assert r.status_code == status.HTTP_200_OK
        assert r.json()["status"] == "canceled"
        reservation.refresh_from_db()
        assert reservation.status == Reservation.Status.CANCELED
        mock_send.delay.assert_called_once_with(reservation.id, "canceled")

    def test_404(self, mock_send, client, user):
        client.force_authenticate(user=user)
        r = client.post("/api/reservations/99999/cancel/")
        assert r.status_code == status.HTTP_404_NOT_FOUND
        mock_send.delay.assert_not_called()
