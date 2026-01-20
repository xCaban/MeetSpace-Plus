"""Wyjątki domenowe aplikacji reservations."""


class ReservationCollisionError(Exception):
    """Kolizja slotu z istniejącą rezerwacją. Mapowany na HTTP 409."""

    pass


class ReservationValidationError(Exception):
    """Błąd walidacji (np. start >= end, poza godzinami roboczymi). Mapowany na HTTP 400."""

    pass
