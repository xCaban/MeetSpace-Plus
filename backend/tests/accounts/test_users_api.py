"""Testy API zarządzania użytkownikami (admin)."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Role, User, UserRole


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def role_user(db):
    return Role.objects.get_or_create(name="user")[0]


@pytest.fixture
def role_admin(db):
    return Role.objects.get_or_create(name="admin")[0]


@pytest.fixture
def admin_user(db, role_admin, role_user):
    u = User.objects.create_user(username="admin@ex.com", password="test", email="admin@ex.com")
    UserRole.objects.get_or_create(user=u, role=role_admin)
    UserRole.objects.get_or_create(user=u, role=role_user)
    return u


@pytest.fixture
def regular_user(db, role_user):
    u = User.objects.create_user(
        username="user@ex.com",
        password="test",
        email="user@ex.com",
        first_name="Jan",
        last_name="Kowalski",
    )
    UserRole.objects.get_or_create(user=u, role=role_user)
    return u


@pytest.mark.django_db
class TestUserListAPI:
    def test_unauthenticated_401(self, client):
        r = client.get("/api/admin/users/")
        assert r.status_code == status.HTTP_401_UNAUTHORIZED

    def test_non_admin_403(self, client, regular_user):
        client.force_authenticate(user=regular_user)
        r = client.get("/api/admin/users/")
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_200(self, client, admin_user, regular_user):
        client.force_authenticate(user=admin_user)
        r = client.get("/api/admin/users/")
        assert r.status_code == status.HTTP_200_OK
        assert len(r.json()) >= 2

    def test_search(self, client, admin_user, regular_user):
        client.force_authenticate(user=admin_user)
        r = client.get("/api/admin/users/", {"search": "Jan"})
        assert r.status_code == status.HTTP_200_OK
        data = r.json()
        assert len(data) == 1
        assert data[0]["email"] == regular_user.email


@pytest.mark.django_db
class TestUserCreateAPI:
    def test_create_user(self, client, admin_user, role_user):
        client.force_authenticate(user=admin_user)
        r = client.post(
            "/api/admin/users/",
            {
                "email": "new@ex.com",
                "password": "SecurePass123!",
                "first_name": "Nowy",
                "last_name": "Uzytkownik",
                "is_admin": False,
            },
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED
        data = r.json()
        assert data["email"] == "new@ex.com"
        assert data["first_name"] == "Nowy"
        assert data["is_admin"] is False

    def test_create_admin_user(self, client, admin_user):
        client.force_authenticate(user=admin_user)
        r = client.post(
            "/api/admin/users/",
            {
                "email": "newadmin@ex.com",
                "password": "SecurePass123!",
                "is_admin": True,
            },
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED
        data = r.json()
        assert data["email"] == "newadmin@ex.com"
        assert data["is_admin"] is True

    def test_duplicate_email_400(self, client, admin_user, regular_user):
        client.force_authenticate(user=admin_user)
        r = client.post(
            "/api/admin/users/",
            {
                "email": regular_user.email,
                "password": "SecurePass123!",
            },
            format="json",
        )
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_weak_password_400(self, client, admin_user):
        client.force_authenticate(user=admin_user)
        r = client.post(
            "/api/admin/users/",
            {
                "email": "weak@ex.com",
                "password": "123",
            },
            format="json",
        )
        assert r.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserUpdateAPI:
    def test_update_user(self, client, admin_user, regular_user):
        client.force_authenticate(user=admin_user)
        r = client.patch(
            f"/api/admin/users/{regular_user.id}/",
            {
                "first_name": "Updated",
                "last_name": "Name",
            },
            format="json",
        )
        assert r.status_code == status.HTTP_200_OK
        regular_user.refresh_from_db()
        assert regular_user.first_name == "Updated"
        assert regular_user.last_name == "Name"

    def test_grant_admin_role(self, client, admin_user, regular_user):
        client.force_authenticate(user=admin_user)
        # Sprawdź, że user nie jest adminem
        assert not Role.objects.filter(userrole__user=regular_user, name="admin").exists()

        r = client.patch(
            f"/api/admin/users/{regular_user.id}/",
            {"is_admin": True},
            format="json",
        )
        assert r.status_code == status.HTTP_200_OK
        assert r.json()["is_admin"] is True
        # Sprawdź w bazie
        assert Role.objects.filter(userrole__user=regular_user, name="admin").exists()

    def test_revoke_admin_role(self, client, admin_user, role_admin, regular_user):
        # Nadaj adminowi
        UserRole.objects.get_or_create(user=regular_user, role=role_admin)
        client.force_authenticate(user=admin_user)

        r = client.patch(
            f"/api/admin/users/{regular_user.id}/",
            {"is_admin": False},
            format="json",
        )
        assert r.status_code == status.HTTP_200_OK
        assert r.json()["is_admin"] is False
        # Sprawdź w bazie
        assert not Role.objects.filter(userrole__user=regular_user, name="admin").exists()


@pytest.mark.django_db
class TestUserDeleteAPI:
    def test_delete_user(self, client, admin_user, regular_user):
        user_id = regular_user.id
        client.force_authenticate(user=admin_user)
        r = client.delete(f"/api/admin/users/{user_id}/")
        assert r.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(id=user_id).exists()

    def test_cannot_delete_self(self, client, admin_user):
        client.force_authenticate(user=admin_user)
        r = client.delete(f"/api/admin/users/{admin_user.id}/")
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        # User nadal istnieje
        assert User.objects.filter(id=admin_user.id).exists()


@pytest.mark.django_db
class TestUserPasswordResetAPI:
    def test_reset_password(self, client, admin_user, regular_user):
        client.force_authenticate(user=admin_user)
        r = client.post(
            f"/api/admin/users/{regular_user.id}/reset-password/",
            {"password": "NewSecurePass456!"},
            format="json",
        )
        assert r.status_code == status.HTTP_200_OK
        regular_user.refresh_from_db()
        assert regular_user.check_password("NewSecurePass456!")

    def test_weak_password_400(self, client, admin_user, regular_user):
        client.force_authenticate(user=admin_user)
        r = client.post(
            f"/api/admin/users/{regular_user.id}/reset-password/",
            {"password": "123"},
            format="json",
        )
        assert r.status_code == status.HTTP_400_BAD_REQUEST
