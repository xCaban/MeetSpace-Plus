"""Testy warstwy services: availability (kolizje) i booking (create_reservation)."""

from datetime import datetime
from unittest.mock import patch

import pytest
from django.utils import timezone

from accounts.models import User
from reservations.exceptions import ReservationCollisionError, ReservationValidationError
from reservations.models import Reservation
from reservations.services.availability import intervals_overlap
from reservations.services.booking import create_reservation
from rooms.models import Room


# --- intervals_overlap: przypadki brzegowe ---


class TestIntervalsOverlap:
    """Przedziały półotwarte [start, end); styczność nie koliduje."""

    def test_styczność_brak_kolizji(self):
        """[9,10) i [10,11) – stykające się; brak nakładania."""
        assert intervals_overlap(
            datetime(2025, 1, 15, 9, 0),
            datetime(2025, 1, 15, 10, 0),
            datetime(2025, 1, 15, 10, 0),
            datetime(2025, 1, 15, 11, 0),
        ) is False

    def test_pełne_zawarcie_kolizja(self):
        """[9,12) zawiera [10,11) – kolizja."""
        assert intervals_overlap(
            datetime(2025, 1, 15, 9, 0),
            datetime(2025, 1, 15, 12, 0),
            datetime(2025, 1, 15, 10, 0),
            datetime(2025, 1, 15, 11, 0),
        ) is True

    def test_identyczne_okna_kolizja(self):
        """[9,10) i [9,10) – identyczne; kolizja."""
        a = datetime(2025, 1, 15, 9, 0), datetime(2025, 1, 15, 10, 0)
        assert intervals_overlap(a[0], a[1], a[0], a[1]) is True

    def test_rozłączne_brak_kolizji(self):
        """[9,10) i [11,12) – rozłączne."""
        assert intervals_overlap(
            datetime(2025, 1, 15, 9, 0),
            datetime(2025, 1, 15, 10, 0),
            datetime(2025, 1, 15, 11, 0),
            datetime(2025, 1, 15, 12, 0),
        ) is False

    def test_częściowe_nakładanie_kolizja(self):
        """[9,11) i [10,12) – częściowe; kolizja."""
        assert intervals_overlap(
            datetime(2025, 1, 15, 9, 0),
            datetime(2025, 1, 15, 11, 0),
            datetime(2025, 1, 15, 10, 0),
            datetime(2025, 1, 15, 12, 0),
        ) is True


# --- create_reservation ---


@pytest.fixture
def user(db):
    return User.objects.create_user(username="u1", password="test", email="u1@ex.com")


@pytest.fixture
def room(db):
    return Room.objects.create(name="Sala A")


@pytest.fixture
def work_hours():
    from datetime import time

    return time(8, 0), time(18, 0)


def _dt(year, month, day, h, m, tz=None):
    if tz is None:
        tz = timezone.get_current_timezone()
    return timezone.make_aware(datetime(year, month, day, h, m), tz)


@patch("reservations.services.booking.expire_hold")
class TestCreateReservation:
    def test_start_ge_end_validation_error(self, mock_expire, user, room, work_hours):
        work_start, work_end = work_hours
        start = _dt(2025, 2, 1, 10, 0)
        end = _dt(2025, 2, 1, 9, 0)
        with pytest.raises(ReservationValidationError, match="start_at"):
            create_reservation(
                user, room.id, start, end, work_start=work_start, work_end=work_end
            )
        mock_expire.apply_async.assert_not_called()

    def test_poza_godzinami_roboczymi(self, mock_expire, user, room, work_hours):
        work_start, work_end = work_hours  # 8–18
        start = _dt(2025, 2, 1, 7, 0)
        end = _dt(2025, 2, 1, 8, 0)
        with pytest.raises(ReservationValidationError, match="godzinami roboczymi"):
            create_reservation(
                user, room.id, start, end, work_start=work_start, work_end=work_end
            )
        mock_expire.apply_async.assert_not_called()

    def test_na_dwa_dni_validation_error(self, mock_expire, user, room, work_hours):
        work_start, work_end = work_hours
        start = _dt(2025, 2, 1, 17, 0)
        end = _dt(2025, 2, 2, 9, 0)
        with pytest.raises(ReservationValidationError, match="jednym dniu"):
            create_reservation(
                user, room.id, start, end, work_start=work_start, work_end=work_end
            )
        mock_expire.apply_async.assert_not_called()

    def test_naive_datetime_validation_error(self, mock_expire, user, room, work_hours):
        work_start, work_end = work_hours
        start = datetime(2025, 2, 1, 10, 0)  # naive
        end = datetime(2025, 2, 1, 11, 0)
        with pytest.raises(ReservationValidationError, match="timezone-aware"):
            create_reservation(
                user, room.id, start, end, work_start=work_start, work_end=work_end
            )
        mock_expire.apply_async.assert_not_called()

    def test_kolizja_collision_error(self, mock_expire, user, room, work_hours):
        work_start, work_end = work_hours
        start = _dt(2025, 2, 1, 10, 0)
        end = _dt(2025, 2, 1, 11, 0)
        Reservation.objects.create(
            user=user, room=room, status=Reservation.Status.CONFIRMED,
            start_at=start, end_at=end
        )
        with pytest.raises(ReservationCollisionError, match="kolizja"):
            create_reservation(
                user, room.id, start, end, work_start=work_start, work_end=work_end
            )
        mock_expire.apply_async.assert_not_called()

    def test_ok_tworzy_pending_i_kolejkuje_expire_hold(
        self, mock_expire, user, room, work_hours
    ):
        work_start, work_end = work_hours
        start = _dt(2025, 2, 1, 10, 0)
        end = _dt(2025, 2, 1, 11, 0)
        r = create_reservation(
            user, room.id, start, end,
            work_start=work_start, work_end=work_end, hold_minutes=15
        )
        assert r.status == Reservation.Status.PENDING
        assert r.room_id == room.id
        assert r.start_at == start and r.end_at == end
        assert r.hold_expires_at is not None
        mock_expire.apply_async.assert_called_once()
        call = mock_expire.apply_async.call_args
        assert call[1]["eta"] == r.hold_expires_at
        assert call[1]["args"][0] == r.id

    def test_brak_kolizji_gdy_styczność(self, mock_expire, user, room, work_hours):
        """Istniejąca [10,11); nowa [11,12) – styczność: brak kolizji."""
        work_start, work_end = work_hours
        Reservation.objects.create(
            user=user, room=room, status=Reservation.Status.CONFIRMED,
            start_at=_dt(2025, 2, 1, 10, 0), end_at=_dt(2025, 2, 1, 11, 0)
        )
        r = create_reservation(
            user, room.id,
            _dt(2025, 2, 1, 11, 0), _dt(2025, 2, 1, 12, 0),
            work_start=work_start, work_end=work_end, hold_minutes=15
        )
        assert r.status == Reservation.Status.PENDING
        mock_expire.apply_async.assert_called_once()
