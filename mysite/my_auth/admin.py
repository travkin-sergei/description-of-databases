# my_auth/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import MyProfile
from rest_framework.authtoken.models import Token


# Регистрируем MyProfile
@admin.register(MyProfile)
class MyProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_approved')


# Меняем UserAdmin для отображения токенов
class CustomUserAdmin(UserAdmin):
    # Просто показываем токен в списке
    list_display = UserAdmin.list_display + ('_get_token',)

    def _get_token(self, obj):
        """Показываем токен пользователя"""
        token = Token.objects.filter(user=obj).first()
        if token:
            return token.key
        return "Нет токена"

    _get_token.short_description = 'API Токен'


# Регистрируем
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
