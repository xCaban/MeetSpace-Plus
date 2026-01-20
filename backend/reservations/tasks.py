"""Zadania Celery: wygaszanie holdów, powiadomienia, reconcile."""

import logging

from celery import shared_task
from django.utils import timezone

from reservations.models import Reservation

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def expire_hold(self, reservation_id):
    """Anuluje rezerwację w statusie pending, jeśli hold wygasł (hold_expires_at <= now).

    Wywoływane z eta=hold_expires_at przy create_reservation.
    Retry przy błędach transjentowych (np. baza).
    """
    try:
        r = Reservation.objects.get(pk=reservation_id)
    except Reservation.DoesNotExist:
        logger.info(
            "expire_hold skip",
            extra={"reservation_id": reservation_id, "reason": "not_found"},
        )
        return

    now = timezone.now()
    if (
        r.status == Reservation.Status.PENDING
        and r.hold_expires_at is not None
        and r.hold_expires_at <= now
    ):
        try:
            r.status = Reservation.Status.CANCELED
            r.save(update_fields=["status", "updated_at"])
            logger.info(
                "expire_hold canceled",
                extra={"reservation_id": reservation_id, "canceled": True},
            )
        except Exception as exc:
            logger.warning(
                "expire_hold retry",
                extra={"reservation_id": reservation_id, "error": str(exc)},
            )
            raise self.retry(exc=exc)
    else:
        logger.info(
            "expire_hold skip",
            extra={
                "reservation_id": reservation_id,
                "reason": "not_pending_or_hold_not_expired",
                "status": r.status,
            },
        )


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def send_notifications(self, reservation_id, event):
    """Dummy: loguje zdarzenie. Hook pod e-mail / WebSocket (do rozbudowy).

    event: np. 'created', 'confirmed', 'canceled', 'hold_expired'.
    """
    logger.info(
        "send_notifications",
        extra={"reservation_id": reservation_id, "event": event},
    )
    # hook: wywołanie pod przyszłe kanały (e-mail, WebSocket)
    # _send_email(reservation_id, event)
    # _push_websocket(reservation_id, event)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def reconcile_pending(self):
    """Sprząta stare pending (hold_expires_at <= now). Wywoływane z Beat co 5 min."""
    now = timezone.now()
    qs = Reservation.objects.filter(
        status=Reservation.Status.PENDING,
        hold_expires_at__isnull=False,
        hold_expires_at__lte=now,
    )
    count = 0
    try:
        for r in qs:
            r.status = Reservation.Status.CANCELED
            r.save(update_fields=["status", "updated_at"])
            count += 1
        logger.info(
            "reconcile_pending done",
            extra={"canceled_count": count},
        )
    except Exception as exc:
        logger.warning(
            "reconcile_pending retry",
            extra={"canceled_so_far": count, "error": str(exc)},
        )
        raise self.retry(exc=exc)
