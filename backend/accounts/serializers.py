from django.contrib.auth import get_user_model

from rest_framework import serializers

from accounts.models import Role

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
