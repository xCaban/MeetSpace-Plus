"""Zadania Celery: wygaszanie holdów, powiadomienia."""

from celery import shared_task

from reservations.models import Reservation


@shared_task
def expire_hold(reservation_id):
    """Anuluje rezerwację w statusie pending, jeśli hold wygasł.

    Wywoływane z eta=hold_expires_at przy create_reservation.
    """
    try:
        r = Reservation.objects.get(pk=reservation_id)
    except Reservation.DoesNotExist:
        return
    if r.status == Reservation.Status.PENDING:
        r.status = Reservation.Status.CANCELED
        r.save(update_fields=["status", "updated_at"])
