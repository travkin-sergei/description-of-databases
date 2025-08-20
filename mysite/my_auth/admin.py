# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import MyProfile


class MyProfileInline(admin.StackedInline):
    model = MyProfile
    can_delete = False
    verbose_name_plural = 'Профили'
    fk_name = 'user'
    fields = 'phone', 'is_approved',


class CustomUserAdmin(UserAdmin):
    inlines = [MyProfileInline]


# Регистрируем UserAdmin с MyProfileInline
admin.site.unregister(User)  # Сначала удаляем стандартный UserAdmin
admin.site.register(User, CustomUserAdmin)  # Затем регистрируем с кастомным UserAdmin


# Убираем дублирование регистрации
@admin.register(MyProfile)
class MyProfileAdmin(admin.ModelAdmin):
    list_display = 'user', 'is_approved',
    list_filter = 'is_approved',
    search_fields = 'user__username',
    actions = ['approve_profiles', 'disapprove_profiles']

    def approve_profiles(self, request, queryset):
        queryset.update(is_approved=True)

    approve_profiles.short_description = "Одобрить выбранные профили"

    def disapprove_profiles(self, request, queryset):
        queryset.update(is_approved=False)

    disapprove_profiles.short_description = "Отклонить выбранные профили"
