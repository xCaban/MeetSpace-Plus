import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from accounts.models import Role, UserRole

User = get_user_model()

DEMO_PASSWORD = os.environ.get("DEMO_PASSWORD", "DemoPass!1")

ADMIN_EMAILS = ["admin1@example.com", "admin2@example.com"]
USER_EMAILS = ["user1@example.com", "user2@example.com", "user3@example.com"]


class Command(BaseCommand):
    help = "Tworzy role admin/user, 2 konta admin oraz kilka kont user (idempotentne)."

    def handle(self, *args, **options):
        role_admin, _ = Role.objects.get_or_create(name="admin")
        role_user, _ = Role.objects.get_or_create(name="user")

        for email in ADMIN_EMAILS:
            u, created = User.objects.get_or_create(
                username=email,
                defaults={
                    "email": email,
                    "is_staff": True,
                    "is_active": True,
                },
            )
            if created:
                u.set_password(DEMO_PASSWORD)
                u.save()
            else:
                if not u.is_staff:
                    u.is_staff = True
                    u.save(update_fields=["is_staff"])
            UserRole.objects.get_or_create(user=u, role=role_admin)
            self.stdout.write(self.style.SUCCESS(f"Admin: {email}"))

        for email in USER_EMAILS:
            u, created = User.objects.get_or_create(
                username=email,
                defaults={
                    "email": email,
                    "is_staff": False,
                    "is_active": True,
                },
            )
            if created:
                u.set_password(DEMO_PASSWORD)
                u.save()
            UserRole.objects.get_or_create(user=u, role=role_user)
            self.stdout.write(self.style.SUCCESS(f"User: {email}"))

        self.stdout.write(self.style.SUCCESS("Hasło (domyślnie): DEMO_PASSWORD=DemoPass!1"))
