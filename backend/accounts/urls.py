from django.urls import path

from accounts.views import (
    LoginView,
    TokenBlacklistDocumentedView,
    TokenRefreshDocumentedView,
)

urlpatterns = [
    path("login", LoginView.as_view(), name="auth-login"),
    path("refresh", TokenRefreshDocumentedView.as_view(), name="auth-refresh"),
    path("logout", TokenBlacklistDocumentedView.as_view(), name="auth-logout"),
]
