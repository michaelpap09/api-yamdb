"""Сериализаторы приложения пользователей."""

from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""

    class Meta:
        """Настройки сериализатора пользователя."""

        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )

    def validate_username(self, value):
        """Проверяет, что username не равен me."""
        if value == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать username "me".'
            )
        return value


class UserMeSerializer(UserSerializer):
    """Сериализатор для профиля текущего пользователя."""

    class Meta(UserSerializer.Meta):
        """Настройки сериализатора текущего пользователя."""

        read_only_fields = ('role',)


class SignupSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователя."""

    username = serializers.CharField(
        max_length=150,
        validators=(UnicodeUsernameValidator(),),
    )
    email = serializers.EmailField(max_length=254)

    def validate_username(self, value):
        """Проверяет, что username не равен me."""
        if value == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать username "me".'
            )
        return value

    def validate(self, data):
        """Проверяет уникальность пары username и email."""
        username = data['username']
        email = data['email']

        user_by_username = User.objects.filter(username=username).first()
        user_by_email = User.objects.filter(email=email).first()

        if user_by_username and user_by_username.email != email:
            raise serializers.ValidationError(
                {'username': 'Пользователь с таким username уже существует.'}
            )

        if user_by_email and user_by_email.username != username:
            raise serializers.ValidationError(
                {'email': 'Пользователь с таким email уже существует.'}
            )

        return data


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения JWT-токена."""

    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()
