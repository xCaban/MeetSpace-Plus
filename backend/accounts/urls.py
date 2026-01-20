from django.urls import path

from accounts.views import LoginView
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView

urlpatterns = [
    path("login", LoginView.as_view(), name="auth-login"),
    path("refresh", TokenRefreshView.as_view(), name="auth-refresh"),
    path("logout", TokenBlacklistView.as_view(), name="auth-logout"),
]
