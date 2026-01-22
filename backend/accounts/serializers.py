from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

from accounts.models import Role, UserRole

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "Nieprawidłowy adres e-mail lub hasło."})
        if not user.check_password(password):
            raise serializers.ValidationError({"email": "Nieprawidłowy adres e-mail lub hasło."})
        if not user.is_active:
            raise serializers.ValidationError({"email": "Konto jest nieaktywne."})
        data["user"] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "roles")

    def get_roles(self, obj):
        return list(Role.objects.filter(userrole__user=obj).values_list("name", flat=True))


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    password_confirm = serializers.CharField(write_only=True, style={"input_type": "password"})
    first_name = serializers.CharField(required=False, allow_blank=True, default="")
    last_name = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Użytkownik z tym adresem e-mail już istnieje.")
        return value.lower()

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Hasła nie są zgodne."})
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user


# --- Admin User Management Serializers ---


class UserListSerializer(serializers.ModelSerializer):
    """Serializer dla listy użytkowników (admin)."""

    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "is_admin", "last_login", "created_at")

    def get_is_admin(self, obj):
        return Role.objects.filter(userrole__user=obj, name="admin").exists()


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer dla szczegółów użytkownika (admin)."""

    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "is_admin",
            "last_login",
            "created_at",
            "updated_at",
        )

    def get_is_admin(self, obj):
        return Role.objects.filter(userrole__user=obj, name="admin").exists()


class UserCreateSerializer(serializers.Serializer):
    """Serializer do tworzenia użytkownika przez admina."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    first_name = serializers.CharField(required=False, allow_blank=True, default="")
    last_name = serializers.CharField(required=False, allow_blank=True, default="")
    is_admin = serializers.BooleanField(required=False, default=False)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Użytkownik z tym adresem e-mail już istnieje.")
        return value.lower()

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        is_admin = validated_data.pop("is_admin", False)
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        # Przypisz rolę "user" domyślnie
        user_role, _ = Role.objects.get_or_create(name="user")
        UserRole.objects.get_or_create(user=user, role=user_role)
        # Przypisz rolę "admin" jeśli zaznaczone
        if is_admin:
            admin_role, _ = Role.objects.get_or_create(name="admin")
            UserRole.objects.get_or_create(user=user, role=admin_role)
        return user


class UserUpdateSerializer(serializers.Serializer):
    """Serializer do aktualizacji użytkownika przez admina."""

    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    is_admin = serializers.BooleanField(required=False)

    def validate_email(self, value):
        if self.instance and User.objects.filter(email__iexact=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("Użytkownik z tym adresem e-mail już istnieje.")
        return value.lower() if value else value

    def update(self, instance, validated_data):
        is_admin = validated_data.pop("is_admin", None)

        if "email" in validated_data:
            instance.email = validated_data["email"]
            instance.username = validated_data["email"]
        if "first_name" in validated_data:
            instance.first_name = validated_data["first_name"]
        if "last_name" in validated_data:
            instance.last_name = validated_data["last_name"]
        instance.save()

        # Aktualizuj rolę admin jeśli przekazano
        if is_admin is not None:
            admin_role, _ = Role.objects.get_or_create(name="admin")
            if is_admin:
                UserRole.objects.get_or_create(user=instance, role=admin_role)
            else:
                UserRole.objects.filter(user=instance, role=admin_role).delete()

        return instance


class AdminPasswordResetSerializer(serializers.Serializer):
    """Serializer do resetowania hasła użytkownika przez admina."""

    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate_password(self, value):
        validate_password(value)
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data["password"])
        instance.save(update_fields=["password"])
        return instance
