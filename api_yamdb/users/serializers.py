"""Сериализаторы приложения пользователей."""

from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

EMAIL_MAX_LENGTH = 254
USERNAME_MAX_LENGTH = 150

User = get_user_model()


def validate_username_not_me(value):
    """Проверяет, что username не равен me."""
    if value == 'me':
        raise serializers.ValidationError(
            'Нельзя использовать username "me".'
        )
    return value


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""

    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        validators=(
            UnicodeUsernameValidator(),
            validate_username_not_me,
            UniqueValidator(queryset=User.objects.all()),
        ),
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class UserMeSerializer(UserSerializer):
    """Сериализатор для профиля текущего пользователя."""

    class Meta(UserSerializer.Meta):
        """Настройки сериализатора текущего пользователя."""

        read_only_fields = ('role',)


class SignupSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователя."""

    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        validators=(UnicodeUsernameValidator(),),
    )
    email = serializers.EmailField(max_length=EMAIL_MAX_LENGTH)

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

        errors = {}
        if user_by_username and user_by_username.email != email:
            errors['username'] = (
                'Пользователь с таким username уже существует.'
            )
        if user_by_email and user_by_email.username != username:
            errors['email'] = 'Пользователь с таким email уже существует.'
        if errors:
            raise serializers.ValidationError(errors)

        return data


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения JWT-токена."""

    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH)
    confirmation_code = serializers.CharField()
