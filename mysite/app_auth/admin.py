from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import MyProfile, RegistrationRequest


class MyUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('link_profile',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительно', {'fields': ('link_profile',)}),
    )


admin.site.register(MyProfile, MyUserAdmin)


@admin.register(RegistrationRequest)
class RegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ('email', 'description', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('email', 'description')