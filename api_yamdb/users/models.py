"""Модели приложения пользователей."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя с ролями и кодом подтверждения."""

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = (
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    )

    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Адрес электронной почты',
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография',
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Роль',
    )
    confirmation_code = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Код подтверждения',
    )

    class Meta:
        """Настройки модели пользователя."""

        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        """Проверяет, есть ли у пользователя права администратора."""
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        """Проверяет, есть ли у пользователя права модератора."""
        return self.role == self.MODERATOR

    @property
    def is_user(self):
        """Проверяет, есть ли у пользователя обычная роль."""
        return self.role == self.USER

    def __str__(self):
        """Возвращает имя пользователя."""
        return self.username
