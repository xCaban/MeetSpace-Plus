"""ViewSet i endpointy REST dla sal."""

from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsAdmin
from rooms.models import Room
from rooms.serializers import (
    RoomCreateUpdateSerializer,
    RoomDetailSerializer,
    RoomListSerializer,
)


@extend_schema_view(
    list=extend_schema(
        tags=["rooms"],
        summary="Lista sal",
        description="Publiczna lista sal. Bez uwierzytelnienia.",
        responses={200: RoomListSerializer(many=True)},
        examples=[
            OpenApiExample(
                "Response",
                value=[
                    {"id": 1, "name": "Sala A", "created_at": "2025-01-01T00:00:00Z", "updated_at": "2025-01-01T00:00:00Z"},
                ],
                response_only=True,
            ),
        ],
    ),
    retrieve=extend_schema(
        tags=["rooms"],
        summary="Szczegóły sali",
        description="Publiczne szczegóły sali (z wyposażeniem). Bez uwierzytelnienia.",
        responses={200: RoomDetailSerializer, 404: {"description": "Nie znaleziono sali"}},
        examples=[
            OpenApiExample(
                "Response",
                value={
                    "id": 1,
                    "name": "Sala A",
                    "equipment": [{"name": "Projektor", "qty": 1}, {"name": "Tablica", "qty": 1}],
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                },
                response_only=True,
            ),
        ],
    ),
    create=extend_schema(
        tags=["rooms"],
        summary="Dodaj salę (admin)",
        description="Tylko admin. Tworzy nową salę.",
        request=RoomCreateUpdateSerializer,
        responses={
            201: RoomDetailSerializer,
            400: {"description": "Błąd walidacji"},
            401: {"description": "Brak uwierzytelnienia"},
            403: {"description": "Brak uprawnień (wymagana rola admin)"},
        },
        examples=[
            OpenApiExample("Przykład", value={"name": "Sala A"}, request_only=True),
        ],
    ),
    partial_update=extend_schema(
        tags=["rooms"],
        summary="Aktualizuj salę (admin)",
        description="Tylko admin. Częściowa aktualizacja (PATCH).",
        request=RoomCreateUpdateSerializer,
        responses={
            200: RoomDetailSerializer,
            400: {"description": "Błąd walidacji"},
            401: {"description": "Brak uwierzytelnienia"},
            403: {"description": "Brak uprawnień"},
            404: {"description": "Nie znaleziono sali"},
        },
        examples=[
            OpenApiExample(
                "Przykład PATCH", value={"name": "Sala A – zaktualizowana"}, request_only=True
            ),
        ],
    ),
    destroy=extend_schema(
        tags=["rooms"],
        summary="Usuń salę (admin)",
        description="Tylko admin.",
        responses={
            204: {"description": "Usunięto"},
            401: {"description": "Brak uwierzytelnienia"},
            403: {"description": "Brak uprawnień"},
            404: {"description": "Nie znaleziono sali"},
        },
    ),
)
class RoomViewSet(ModelViewSet):
    queryset = Room.objects.all().prefetch_related("roomequipment_set__equipment")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return RoomDetailSerializer
        if self.action in ("create", "partial_update", "update"):
            return RoomCreateUpdateSerializer
        return RoomListSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAdmin()]

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        room = ser.save()
        return Response(
            RoomDetailSerializer(room).data,
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        ser = self.get_serializer(instance, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        room = ser.save()
        return Response(RoomDetailSerializer(room).data)

    def update(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
