"""Testy zadań Celery: expire_hold, send_notifications, reconcile_pending."""

from datetime import timedelta

from django.utils import timezone

import pytest

from accounts.models import User
from reservations.models import Reservation
from reservations.tasks import expire_hold, reconcile_pending, send_notifications
from rooms.models import Room


@pytest.fixture
def user(db):
    return User.objects.create_user(username="u1", password="test", email="u1@ex.com")


@pytest.fixture
def room(db):
    return Room.objects.create(name="Sala A")


def _dt_offset(minutes=0):
    return timezone.now() + timedelta(minutes=minutes)


@pytest.mark.django_db
class TestExpireHold:
    """expire_hold: anuluje tylko pending z hold_expires_at <= now."""

    def test_pending_hold_expired_cancels(self, user, room):
        past = _dt_offset(-10)
        r = Reservation.objects.create(
            user=user,
            room=room,
            status=Reservation.Status.PENDING,
            start_at=_dt_offset(60),
            end_at=_dt_offset(120),
            hold_expires_at=past,
        )
        expire_hold(r.id)
        r.refresh_from_db()
        assert r.status == Reservation.Status.CANCELED

    def test_pending_hold_not_expired_no_change(self, user, room):
        future = _dt_offset(10)
        r = Reservation.objects.create(
            user=user,
            room=room,
            status=Reservation.Status.PENDING,
            start_at=_dt_offset(60),
            end_at=_dt_offset(120),
            hold_expires_at=future,
        )
        expire_hold(r.id)
        r.refresh_from_db()
        assert r.status == Reservation.Status.PENDING

    def test_pending_hold_expires_at_none_no_change(self, user, room):
        r = Reservation.objects.create(
            user=user,
            room=room,
            status=Reservation.Status.PENDING,
            start_at=_dt_offset(60),
            end_at=_dt_offset(120),
            hold_expires_at=None,
        )
        expire_hold(r.id)
        r.refresh_from_db()
        assert r.status == Reservation.Status.PENDING

    def test_confirmed_no_change_even_if_hold_expired(self, user, room):
        past = _dt_offset(-10)
        r = Reservation.objects.create(
            user=user,
            room=room,
            status=Reservation.Status.CONFIRMED,
            start_at=_dt_offset(60),
            end_at=_dt_offset(120),
            hold_expires_at=past,
        )
        expire_hold(r.id)
        r.refresh_from_db()
        assert r.status == Reservation.Status.CONFIRMED

    def test_not_found_no_error(self):
        expire_hold(99999)  # brak błędu, wczesny return


@pytest.mark.django_db
class TestSendNotifications:
    def test_runs_without_error(self, user, room):
        r = Reservation.objects.create(
            user=user,
            room=room,
            status=Reservation.Status.PENDING,
            start_at=_dt_offset(60),
            end_at=_dt_offset(120),
        )
        send_notifications(r.id, "created")  # dummy: log + hook; nie rzuca


@pytest.mark.django_db
class TestReconcilePending:
    """reconcile_pending: sprząta PENDING z hold_expires_at <= now."""

    def test_cancels_expired_pending(self, user, room):
        past = _dt_offset(-5)
        r = Reservation.objects.create(
            user=user,
            room=room,
            status=Reservation.Status.PENDING,
            start_at=_dt_offset(60),
            end_at=_dt_offset(120),
            hold_expires_at=past,
        )
        reconcile_pending()
        r.refresh_from_db()
        assert r.status == Reservation.Status.CANCELED

    def test_skips_pending_with_future_hold(self, user, room):
        future = _dt_offset(10)
        r = Reservation.objects.create(
            user=user,
            room=room,
            status=Reservation.Status.PENDING,
            start_at=_dt_offset(60),
            end_at=_dt_offset(120),
            hold_expires_at=future,
        )
        reconcile_pending()
        r.refresh_from_db()
        assert r.status == Reservation.Status.PENDING

    def test_skips_pending_with_null_hold(self, user, room):
        r = Reservation.objects.create(
            user=user,
            room=room,
            status=Reservation.Status.PENDING,
            start_at=_dt_offset(60),
            end_at=_dt_offset(120),
            hold_expires_at=None,
        )
        reconcile_pending()
        r.refresh_from_db()
        assert r.status == Reservation.Status.PENDING

    def test_skips_confirmed(self, user, room):
        past = _dt_offset(-5)
        r = Reservation.objects.create(
            user=user,
            room=room,
            status=Reservation.Status.CONFIRMED,
            start_at=_dt_offset(60),
            end_at=_dt_offset(120),
            hold_expires_at=past,
        )
        reconcile_pending()
        r.refresh_from_db()
        assert r.status == Reservation.Status.CONFIRMED
