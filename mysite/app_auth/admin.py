# app_auth/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import MyProfile


class MyUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('link_profile', 'gender',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {'fields': ('link_profile', 'gender',)}),
    )


admin.site.register(MyProfile, MyUserAdmin)
