from django.urls import path

from accounts.views import LoginView, MeView
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView

urlpatterns = [
    path("auth/login", LoginView.as_view(), name="auth-login"),
    path("auth/refresh", TokenRefreshView.as_view(), name="auth-refresh"),
    path("auth/logout", TokenBlacklistView.as_view(), name="auth-logout"),
    path("me", MeView.as_view(), name="me"),
]
