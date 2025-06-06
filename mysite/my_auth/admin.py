from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.timezone import now, timedelta
from .models import MyProfile

class MyProfileInline(admin.StackedInline):
    model = MyProfile
    can_delete = False
    verbose_name_plural = 'Дополнительная информация'
    fields = ('phone', 'is_approved')

class CustomUserAdmin(UserAdmin):
    inlines = [MyProfileInline]
    list_display = UserAdmin.list_display + ('last_login',)

class UserStatsAdmin(admin.ModelAdmin):
    change_list_template = 'admin/user_stats.html'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update({
            'total_users': User.objects.count(),
            'logged_in_today': User.objects.filter(
                last_login__gte=now() - timedelta(days=1)
            ).count()
        })
        return super().changelist_view(request, extra_context)

# Регистрация моделей
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)  # Основная регистрация
admin.site.register(MyProfile)  # Отдельная регистрация профиля

