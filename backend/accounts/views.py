from django.contrib.auth import get_user_model
from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView

from accounts.models import Role, UserRole
from accounts.permissions import IsAdmin
from accounts.serializers import (
    AdminPasswordResetSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserCreateSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
)

User = get_user_model()


@extend_schema_view(
    post=extend_schema(
        tags=["auth"],
        summary="Odśwież token JWT",
        description="Wymaga refresh tokena w body. Zwraca nowy access token. Używaj po wygaśnięciu access (np. 401).",
        request=inline_serializer(
            name="TokenRefreshRequest",
            fields={"refresh": serializers.CharField(help_text="Refresh token JWT")},
        ),
        responses={
            200: inline_serializer(
                name="TokenRefreshResponse",
                fields={"access": serializers.CharField(help_text="Nowy access token")},
            ),
            401: {"description": "Nieprawidłowy lub wygasły refresh token"},
        },
        examples=[
            OpenApiExample(
                "Request", value={"refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."}, request_only=True
            ),
            OpenApiExample(
                "Response", value={"access": "eyJ0eXAiOiJKV1QiLCJhbGc..."}, response_only=True
            ),
        ],
    ),
)
class TokenRefreshDocumentedView(TokenRefreshView):
    """TokenRefreshView z opisem i przykładami w Swaggerze."""


@extend_schema_view(
    post=extend_schema(
        tags=["auth"],
        summary="Wylogowanie (blacklist refresh)",
        description="Dodaje refresh token do blacklisty. Po wywołaniu refresh nie może być już użyty. Dla SPA przy logout.",
        request=inline_serializer(
            name="TokenBlacklistRequest",
            fields={"refresh": serializers.CharField(help_text="Refresh token do unieważnienia")},
        ),
        responses={
            200: {"description": "Token dodany do blacklisty"},
            400: {"description": "Błąd (np. brak refresh w body)"},
        },
        examples=[
            OpenApiExample(
                "Request", value={"refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."}, request_only=True
            ),
        ],
    ),
)
class TokenBlacklistDocumentedView(TokenBlacklistView):
    """TokenBlacklistView z opisem i przykładami w Swaggerze."""


@extend_schema(tags=["auth"])
class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Logowanie (JWT)",
        description="Zwraca access i refresh token oraz profil użytkownika. Używane przez SPA do uwierzytelniania.",
        request=LoginSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "access": {"type": "string", "description": "Token JWT (access)"},
                    "refresh": {"type": "string", "description": "Token do odświeżania"},
                    "user": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "email": {"type": "string"},
                            "first_name": {"type": "string"},
                            "last_name": {"type": "string"},
                            "roles": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                },
            },
            400: {"description": "Błąd walidacji (np. błędne dane logowania)"},
        },
        examples=[
            OpenApiExample(
                "Request",
                value={"email": "user@example.com", "password": "secret123"},
                request_only=True,
            ),
            OpenApiExample(
                "Response",
                value={
                    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                    "user": {
                        "id": 1,
                        "email": "user@example.com",
                        "first_name": "Jan",
                        "last_name": "Kowalski",
                        "roles": ["user"],
                    },
                },
                response_only=True,
            ),
        ],
    )
    def post(self, request):
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserProfileSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["auth"])
class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Rejestracja nowego użytkownika",
        description="Tworzy nowego użytkownika i zwraca tokeny JWT oraz profil. Użytkownik jest aktywny od razu.",
        request=RegisterSerializer,
        responses={
            201: {
                "type": "object",
                "properties": {
                    "access": {"type": "string", "description": "Token JWT (access)"},
                    "refresh": {"type": "string", "description": "Token do odświeżania"},
                    "user": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "email": {"type": "string"},
                            "first_name": {"type": "string"},
                            "last_name": {"type": "string"},
                            "roles": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                },
            },
            400: {"description": "Błąd walidacji (np. email zajęty, hasła nie pasują)"},
        },
        examples=[
            OpenApiExample(
                "Request",
                value={
                    "email": "newuser@example.com",
                    "password": "SecurePass123!",
                    "password_confirm": "SecurePass123!",
                    "first_name": "Jan",
                    "last_name": "Kowalski",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Response",
                value={
                    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                    "user": {
                        "id": 2,
                        "email": "newuser@example.com",
                        "first_name": "Jan",
                        "last_name": "Kowalski",
                        "roles": ["user"],
                    },
                },
                response_only=True,
            ),
        ],
    )
    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()

        # Przypisz domyślną rolę "user"
        user_role, _ = Role.objects.get_or_create(name="user")
        UserRole.objects.get_or_create(user=user, role=user_role)

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserProfileSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["auth"])
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Profil zalogowanego użytkownika",
        description="Wymaga nagłówka Authorization: Bearer <access_token>. Zwraca dane użytkownika i role.",
        responses={
            200: UserProfileSerializer,
            401: {"description": "Brak lub nieprawidłowy token JWT"},
        },
        examples=[
            OpenApiExample(
                "Response",
                value={
                    "id": 1,
                    "email": "user@example.com",
                    "first_name": "Jan",
                    "last_name": "Kowalski",
                    "roles": ["user"],
                },
                response_only=True,
            ),
        ],
    )
    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)


# --- Admin User Management ---


@extend_schema_view(
    list=extend_schema(
        tags=["admin-users"],
        summary="Lista użytkowników (admin)",
        description="Zwraca listę wszystkich użytkowników. Wymaga roli admin.",
        responses={200: UserListSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=["admin-users"],
        summary="Szczegóły użytkownika (admin)",
        responses={200: UserDetailSerializer, 404: {"description": "Nie znaleziono użytkownika"}},
    ),
    create=extend_schema(
        tags=["admin-users"],
        summary="Utwórz użytkownika (admin)",
        request=UserCreateSerializer,
        responses={
            201: UserDetailSerializer,
            400: {"description": "Błąd walidacji"},
            401: {"description": "Brak uwierzytelnienia"},
            403: {"description": "Brak uprawnień (wymagana rola admin)"},
        },
    ),
    partial_update=extend_schema(
        tags=["admin-users"],
        summary="Aktualizuj użytkownika (admin)",
        request=UserUpdateSerializer,
        responses={
            200: UserDetailSerializer,
            400: {"description": "Błąd walidacji"},
            401: {"description": "Brak uwierzytelnienia"},
            403: {"description": "Brak uprawnień"},
            404: {"description": "Nie znaleziono użytkownika"},
        },
    ),
    destroy=extend_schema(
        tags=["admin-users"],
        summary="Usuń użytkownika (admin)",
        responses={
            204: {"description": "Usunięto"},
            400: {"description": "Nie można usunąć samego siebie"},
            401: {"description": "Brak uwierzytelnienia"},
            403: {"description": "Brak uprawnień"},
            404: {"description": "Nie znaleziono użytkownika"},
        },
    ),
)
class UserViewSet(ModelViewSet):
    """ViewSet do zarządzania użytkownikami (admin-only)."""

    queryset = User.objects.all().order_by("-created_at")
    permission_classes = [IsAdmin]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["email", "first_name", "last_name"]
    ordering_fields = ["email", "created_at", "last_login"]

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        if self.action == "retrieve":
            return UserDetailSerializer
        if self.action == "create":
            return UserCreateSerializer
        if self.action in ("partial_update", "update"):
            return UserUpdateSerializer
        if self.action == "reset_password":
            return AdminPasswordResetSerializer
        return UserDetailSerializer

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        return Response(UserDetailSerializer(user).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        ser = self.get_serializer(instance, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        user = ser.update(instance, ser.validated_data)
        return Response(UserDetailSerializer(user).data)

    def update(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Nie pozwól adminowi usunąć samego siebie
        if instance.id == request.user.id:
            return Response(
                {"detail": "Nie można usunąć własnego konta."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        tags=["admin-users"],
        summary="Resetuj hasło użytkownika (admin)",
        request=AdminPasswordResetSerializer,
        responses={
            200: {"description": "Hasło zmienione"},
            400: {"description": "Błąd walidacji hasła"},
            401: {"description": "Brak uwierzytelnienia"},
            403: {"description": "Brak uprawnień"},
            404: {"description": "Nie znaleziono użytkownika"},
        },
    )
    @action(detail=True, methods=["post"], url_path="reset-password")
    def reset_password(self, request, pk=None):
        user = self.get_object()
        ser = AdminPasswordResetSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.update(user, ser.validated_data)
        return Response({"detail": "Hasło zostało zmienione."})
