"""Funkcje do wykrywania kolizji (przecięcia przedziałów czasu).

Konwencja: przedziały półotwarte [start, end) – stykające się sloty
(np. [9:00, 10:00) i [10:00, 11:00)) nie kolidują.
"""


def intervals_overlap(
    start_a,
    end_a,
    start_b,
    end_b,
):
    """Sprawdza, czy przedziały [start_a, end_a) i [start_b, end_b) się nakładają.

    Dla półotwartych [a,b) i [c,d): nakładanie zachodzi wtw a < d i c < b.
    Styczność (end_a == start_b lub end_b == start_a) → brak kolizji.
    """
    return start_a < end_b and start_b < end_a
