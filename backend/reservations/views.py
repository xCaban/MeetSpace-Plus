"""ViewSet i endpointy REST dla rezerwacji."""

from django.utils.dateparse import parse_datetime

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsOwnerOrAdmin
from reservations.exceptions import ReservationCollisionError, ReservationValidationError
from reservations.models import Reservation
from reservations.serializers import (
    ReservationCreateSerializer,
    ReservationDetailSerializer,
    ReservationListSerializer,
)
from reservations.services.booking import (
    cancel_reservation,
    confirm_reservation,
    create_reservation,
)


@extend_schema_view(
    list=extend_schema(
        tags=["reservations"],
        summary="Lista rezerwacji",
        description="Lista z filtrami: room_id, from (start_at__gte), to (end_at__lte), status. Wymaga uwierzytelnienia.",
        parameters=[
            OpenApiParameter("room_id", int, OpenApiParameter.QUERY, required=False),
            OpenApiParameter(
                "mine",
                str,
                OpenApiParameter.QUERY,
                required=False,
                description="Jeśli 'true' lub '1', tylko rezerwacje zalogowanego użytkownika.",
            ),
            OpenApiParameter(
                "from",
                str,
                OpenApiParameter.QUERY,
                required=False,
                description="ISO 8601, np. 2025-01-15T08:00:00Z",
            ),
            OpenApiParameter(
                "to",
                str,
                OpenApiParameter.QUERY,
                required=False,
                description="ISO 8601, np. 2025-01-15T18:00:00Z",
            ),
            OpenApiParameter(
                "status",
                str,
                OpenApiParameter.QUERY,
                required=False,
                enum=["pending", "confirmed", "canceled"],
            ),
        ],
        responses={
            200: ReservationListSerializer(many=True),
            401: {"description": "Brak uwierzytelnienia"},
        },
        examples=[
            OpenApiExample(
                "Response",
                value=[
                    {
                        "id": 1,
                        "user": 1,
                        "user_email": "user@example.com",
                        "room": 1,
                        "room_name": "Sala A",
                        "status": "confirmed",
                        "start_at": "2025-01-15T09:00:00+01:00",
                        "end_at": "2025-01-15T10:00:00+01:00",
                        "hold_expires_at": None,
                        "created_at": "2025-01-14T12:00:00Z",
                        "updated_at": "2025-01-14T12:05:00Z",
                    },
                ],
                response_only=True,
            ),
        ],
    ),
    retrieve=extend_schema(
        tags=["reservations"],
        summary="Szczegóły rezerwacji",
        description="Właściciel lub admin.",
        responses={
            200: ReservationDetailSerializer,
            401: {"description": "Brak uwierzytelnienia"},
            403: {"description": "Brak uprawnień"},
            404: {"description": "Nie znaleziono rezerwacji"},
        },
        examples=[
            OpenApiExample(
                "Response",
                value={
                    "id": 1,
                    "user": 1,
                    "user_email": "user@example.com",
                    "room": 1,
                    "room_name": "Sala A",
                    "status": "confirmed",
                    "start_at": "2025-01-15T09:00:00+01:00",
                    "end_at": "2025-01-15T10:00:00+01:00",
                    "hold_expires_at": None,
                    "created_at": "2025-01-14T12:00:00Z",
                    "updated_at": "2025-01-14T12:05:00Z",
                },
                response_only=True,
            ),
        ],
    ),
    create=extend_schema(
        tags=["reservations"],
        summary="Utwórz rezerwację",
        description="Tworzy rezerwację (pending), ustawia hold 15 min, planuje expire_hold. Wymaga uwierzytelnienia.",
        request=ReservationCreateSerializer,
        responses={
            201: ReservationDetailSerializer,
            400: {"description": "Błąd walidacji"},
            401: {"description": "Brak uwierzytelnienia"},
            404: {"description": "Nie znaleziono sali"},
            409: {"description": "Kolizja slotu (room_id, [start_at, end_at])"},
        },
        examples=[
            OpenApiExample(
                "Przykład",
                value={
                    "room_id": 1,
                    "start_at": "2025-01-15T09:00:00+01:00",
                    "end_at": "2025-01-15T10:00:00+01:00",
                },
                request_only=True,
            ),
        ],
    ),
    confirm=extend_schema(
        tags=["reservations"],
        summary="Potwierdź rezerwację",
        description="POST /reservations/{id}/confirm. Właściciel lub admin. pending → confirmed.",
        request=None,
        responses={
            200: ReservationDetailSerializer,
            400: {"description": "Błąd walidacji (np. nie pending)"},
            401: {"description": "Brak uwierzytelnienia"},
            403: {"description": "Brak uprawnień"},
            404: {"description": "Nie znaleziono rezerwacji"},
        },
        examples=[
            OpenApiExample(
                "Response",
                value={
                    "id": 1,
                    "user": 1,
                    "user_email": "user@example.com",
                    "room": 1,
                    "room_name": "Sala A",
                    "status": "confirmed",
                    "start_at": "2025-01-15T09:00:00+01:00",
                    "end_at": "2025-01-15T10:00:00+01:00",
                    "hold_expires_at": None,
                    "created_at": "2025-01-14T12:00:00Z",
                    "updated_at": "2025-01-14T12:05:00Z",
                },
                response_only=True,
            ),
        ],
    ),
    cancel=extend_schema(
        tags=["reservations"],
        summary="Anuluj rezerwację",
        description="POST /reservations/{id}/cancel. Właściciel lub admin. pending/confirmed → canceled.",
        request=None,
        responses={
            200: ReservationDetailSerializer,
            400: {"description": "Błąd walidacji"},
            401: {"description": "Brak uwierzytelnienia"},
            403: {"description": "Brak uprawnień"},
            404: {"description": "Nie znaleziono rezerwacji"},
        },
        examples=[
            OpenApiExample(
                "Response",
                value={
                    "id": 1,
                    "user": 1,
                    "user_email": "user@example.com",
                    "room": 1,
                    "room_name": "Sala A",
                    "status": "canceled",
                    "start_at": "2025-01-15T09:00:00+01:00",
                    "end_at": "2025-01-15T10:00:00+01:00",
                    "hold_expires_at": None,
                    "created_at": "2025-01-14T12:00:00Z",
                    "updated_at": "2025-01-14T12:10:00Z",
                },
                response_only=True,
            ),
        ],
    ),
)
class ReservationViewSet(ModelViewSet):
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        qs = Reservation.objects.select_related("room", "user").order_by("-start_at")
        # Filtry: room_id, from (start_at__gte), to (end_at__lte), status
        room_id = self.request.query_params.get("room_id")
        if room_id is not None:
            try:
                qs = qs.filter(room_id=int(room_id))
            except ValueError:
                pass
        from_ = self.request.query_params.get("from")
        if from_:
            dt = parse_datetime(from_)
            if dt is not None:
                qs = qs.filter(start_at__gte=dt)
        to_ = self.request.query_params.get("to")
        if to_:
            dt = parse_datetime(to_)
            if dt is not None:
                qs = qs.filter(end_at__lte=dt)
        status_ = self.request.query_params.get("status")
        if status_ and status_ in dict(Reservation.Status.choices):
            qs = qs.filter(status=status_)
        mine = self.request.query_params.get("mine", "").lower()
        if mine in ("true", "1"):
            qs = qs.filter(user=self.request.user)
        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return ReservationCreateSerializer
        return (
            ReservationDetailSerializer if self.action == "retrieve" else ReservationListSerializer
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        ser = ReservationListSerializer(queryset, many=True)
        return Response(ser.data)

    def create(self, request, *args, **kwargs):
        ser = ReservationCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        try:
            reservation = create_reservation(
                user=request.user,
                room_id=data["room_id"],
                start_at=data["start_at"],
                end_at=data["end_at"],
            )
        except ReservationCollisionError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_409_CONFLICT,
            )
        except ReservationValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            ReservationDetailSerializer(reservation).data,
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(ReservationDetailSerializer(instance).data)

    @action(detail=True, methods=["post"], url_path="confirm")
    def confirm(self, request, pk=None):
        reservation = self.get_object()
        try:
            confirm_reservation(reservation)
        except ReservationValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        reservation.refresh_from_db()
        return Response(ReservationDetailSerializer(reservation).data)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        reservation = self.get_object()
        try:
            cancel_reservation(reservation)
        except ReservationValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        reservation.refresh_from_db()
        return Response(ReservationDetailSerializer(reservation).data)
