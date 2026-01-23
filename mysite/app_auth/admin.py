from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import MyProfile, RegistrationRequest


@admin.register(MyProfile)
class MyUserAdmin(UserAdmin):
    # Автокомплит для foreign key поля
    autocomplete_fields = ['url', ]

    # Добавляем ваше поле в fieldsets
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('url',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительно', {'fields': ('url',)}),
    )

    # Поиск по собственным полям
    search_fields = ('username', 'first_name', 'last_name', 'email',)
    list_display_links = ('is_active', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'url')
    list_display = ('is_active', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'url')
    list_filter = ('is_staff', 'is_active', 'date_joined')


@admin.register(RegistrationRequest)
class RegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ('email', 'description', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('email', 'description')
