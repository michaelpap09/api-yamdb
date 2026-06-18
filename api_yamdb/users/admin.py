"""Настройки админ-панели для приложения пользователей."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Настройки отображения кастомной модели пользователя в админке."""

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'is_staff',
        'is_superuser',
        'is_active',
    )
    list_filter = (
        'role',
        'is_staff',
        'is_superuser',
        'is_active',
    )
    search_fields = (
        'username',
        'email',
    )
    ordering = ('id',)

    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительные поля', {
            'fields': (
                'bio',
                'role',
                'confirmation_code',
            )
        }),
    )
