"""Agregacja ścieżek API: auth, me, rooms, reservations."""

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from accounts import urls as accounts_urls
from accounts.views import MeView, UserViewSet
from reservations.views import ReservationViewSet
from rooms.views import EquipmentViewSet, RoomViewSet

router = DefaultRouter()
router.register(r"rooms", RoomViewSet, basename="room")
router.register(r"reservations", ReservationViewSet, basename="reservation")
router.register(r"equipment", EquipmentViewSet, basename="equipment")
router.register(r"admin/users", UserViewSet, basename="admin-user")

urlpatterns = [
    path("auth/", include(accounts_urls)),
    path("me", MeView.as_view(), name="me"),
    path("", include(router.urls)),
]
