from django.urls import path

from accounts.views import (
    LoginView,
    RegisterView,
    TokenBlacklistDocumentedView,
    TokenRefreshDocumentedView,
)

urlpatterns = [
    path("login", LoginView.as_view(), name="auth-login"),
    path("register", RegisterView.as_view(), name="auth-register"),
    path("refresh", TokenRefreshDocumentedView.as_view(), name="auth-refresh"),
    path("logout", TokenBlacklistDocumentedView.as_view(), name="auth-logout"),
]
