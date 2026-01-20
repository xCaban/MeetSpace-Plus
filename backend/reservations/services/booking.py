"""Logika tworzenia rezerwacji: walidacja, kolizje, hold, Celery."""

from datetime import timedelta, time

from django.conf import settings
from django.utils import timezone

from reservations.exceptions import ReservationCollisionError, ReservationValidationError
from reservations.models import Reservation
from reservations.services.availability import intervals_overlap
from reservations.tasks import expire_hold, send_notifications


def create_reservation(
    user,
    room_id,
    start_at,
    end_at,
    *,
    work_start=None,
    work_end=None,
    hold_minutes=None,
):
    """Tworzy rezerwację (status=pending, hold 15 min) i kolejkowuje expire_hold.

    - Waliduje: start < end, przedział w godzinach roboczych.
    - Sprawdza kolizje z istniejącymi (nie-anulowanymi); przy kolizji → ReservationCollisionError (409).
    - Ustawia hold_expires_at=now+15min i publikuje expire_hold(reservation_id, eta=hold_expires_at).

    work_start, work_end: datetime.time (domyślnie z settings).
    hold_minutes: int (domyślnie RESERVATION_HOLD_MINUTES).
    """
    work_start = work_start or getattr(settings, "RESERVATION_WORK_START", time(8, 0))
    work_end = work_end or getattr(settings, "RESERVATION_WORK_END", time(18, 0))
    hold_min = (
        hold_minutes
        if hold_minutes is not None
        else getattr(settings, "RESERVATION_HOLD_MINUTES", 15)
    )

    if start_at >= end_at:
        raise ReservationValidationError("start_at musi być wcześniej niż end_at")

    if start_at.date() != end_at.date():
        raise ReservationValidationError(
            "rezerwacja musi mieścić się w jednym dniu"
        )

    if start_at.tzinfo is None or end_at.tzinfo is None:
        raise ReservationValidationError("start_at i end_at muszą być timezone-aware")

    st = start_at.time()
    et = end_at.time()
    if st < work_start or et > work_end:
        raise ReservationValidationError(
            f"rezerwacja poza godzinami roboczymi ({work_start}–{work_end})"
        )

    for r in Reservation.objects.filter(room_id=room_id).exclude(
        status=Reservation.Status.CANCELED
    ):
        if intervals_overlap(start_at, end_at, r.start_at, r.end_at):
            raise ReservationCollisionError(
                f"kolizja z rezerwacją id={r.id} w sali room_id={room_id}"
            )

    now = timezone.now()
    hold_expires_at = now + timedelta(minutes=hold_min)

    reservation = Reservation.objects.create(
        user=user,
        room_id=room_id,
        status=Reservation.Status.PENDING,
        start_at=start_at,
        end_at=end_at,
        hold_expires_at=hold_expires_at,
    )
    expire_hold.apply_async(args=[reservation.id], eta=hold_expires_at)
    return reservation


def confirm_reservation(reservation):
    """Potwierdza rezerwację (pending → confirmed). Kolejkuje send_notifications.

    Uprawnienia (owner lub admin) weryfikuje warstwa widoków.
    """
    if reservation.status != Reservation.Status.PENDING:
        raise ReservationValidationError(
            "Tylko rezerwacje w statusie pending można potwierdzić"
        )
    reservation.status = Reservation.Status.CONFIRMED
    reservation.save(update_fields=["status", "updated_at"])
    send_notifications.delay(reservation.id, "confirmed")
    return reservation


def cancel_reservation(reservation):
    """Anuluje rezerwację (pending/confirmed → canceled). Kolejkuje send_notifications.

    Idempotentne przy już anulowanej. Uprawnienia (owner lub admin) weryfikuje warstwa widoków.
    """
    if reservation.status == Reservation.Status.CANCELED:
        return reservation
    if reservation.status not in (
        Reservation.Status.PENDING,
        Reservation.Status.CONFIRMED,
    ):
        raise ReservationValidationError(
            f"Nie można anulować rezerwacji w statusie {reservation.status}"
        )
    reservation.status = Reservation.Status.CANCELED
    reservation.save(update_fields=["status", "updated_at"])
    send_notifications.delay(reservation.id, "canceled")
    return reservation
