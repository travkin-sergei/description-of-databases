# my_auth/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db.models import Sum
from rest_framework.authtoken.models import Token
from .models import MyProfile, UserLoginStats


class MyProfileInline(admin.StackedInline):
    """
    Inline-модель для отображения профиля в админке пользователя.

    Позволяет просматривать и редактировать связанный профиль
    непосредственно на странице редактирования пользователя.
    """
    model = MyProfile
    can_delete = False
    verbose_name = "Профиль пользователя"
    verbose_name_plural = "Профиль пользователя"
    fields = ('is_approved', 'link_profile', 'created_at')
    readonly_fields = ('created_at',)
    extra = 0


@admin.register(MyProfile)
class MyProfileAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели MyProfile."""

    list_display = ('user', 'is_approved', 'created_at')
    list_display_links = ('user',)
    list_editable = ('is_approved',)
    list_filter = ('is_approved', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__first_name',
                     'user__last_name', 'link_profile')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

    # Автодополнение для поля user - выпадающий список с поиском
    autocomplete_fields = ['user']

    fieldsets = (
        (None, {
            'fields': ('user', 'is_approved')
        }),
        ('Дополнительная информация', {
            'fields': ('link_profile', 'created_at'),
            'classes': ('collapse',)
        }),
    )


class CustomUserAdmin(BaseUserAdmin):
    """Кастомизированный административный интерфейс для модели User."""

    # Добавляем inline-модель профиля
    inlines = [MyProfileInline]

    # Расширяем список отображаемых полей
    list_display = BaseUserAdmin.list_display + ('_get_token', '_get_is_approved',
                                                 '_get_login_count')
    list_select_related = ('profile',)

    # Расширяем поля для поиска (для автодополнения)
    search_fields = ('username', 'email', 'first_name', 'last_name',
                     'profile__link_profile')

    # Добавляем фильтры
    list_filter = BaseUserAdmin.list_filter + ('profile__is_approved',)

    # Добавляем действия
    actions = ['approve_users', 'disapprove_users']

    def get_search_results(self, request, queryset, search_term):
        """
        Расширенный поиск пользователей.

        Позволяет искать пользователей по:
        - Стандартным полям User (username, email, имя, фамилия)
        - Полю link_profile в связанном MyProfile
        - Значению is_approved в профиле (да/нет)
        """
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        # Если поиск по стандартным полям не дал результатов, ищем по профилю
        if not queryset.exists() and search_term:
            # Поиск по is_approved
            if search_term.lower() in ['да', 'yes', 'true', '1', 'одобрен', 'approved']:
                queryset = User.objects.filter(profile__is_approved=True)
            elif search_term.lower() in ['нет', 'no', 'false', '0', 'неодобрен', 'не одобрен']:
                queryset = User.objects.filter(profile__is_approved=False)
            # Поиск по link_profile
            elif '://' in search_term or '.' in search_term:
                profile_queryset = MyProfile.objects.filter(
                    link_profile__icontains=search_term
                )
                user_ids = profile_queryset.values_list('user_id', flat=True)
                queryset = User.objects.filter(id__in=user_ids)

        return queryset, use_distinct

    @admin.display(description='Токен', ordering='auth_token__key')
    def _get_token(self, obj):
        """Отображает первые 12 символов токена пользователя."""
        token = Token.objects.filter(user=obj).first()
        return token.key[:12] + '...' if token else "—"

    @admin.display(description='Одобрен', boolean=True)
    def _get_is_approved(self, obj):
        """Отображает статус одобрения пользователя."""
        return obj.profile.is_approved if hasattr(obj, 'profile') else False

    @admin.display(description='Входов')
    def _get_login_count(self, obj):
        """Отображает общее количество входов пользователя."""
        total_logins = UserLoginStats.objects.filter(user=obj).aggregate(
            total=Sum('login_count')
        )['total']
        return total_logins or 0

    @admin.action(description='Одобрить выбранных пользователей')
    def approve_users(self, request, queryset):
        """Действие для одобрения выбранных пользователей."""
        for user in queryset:
            profile, created = MyProfile.objects.get_or_create(user=user)
            profile.is_approved = True
            profile.save()
        self.message_user(request, f'Одобрено пользователей: {queryset.count()}')

    @admin.action(description='Снять одобрение с выбранных пользователей')
    def disapprove_users(self, request, queryset):
        """Действие для снятия одобрения с выбранных пользователей."""
        for user in queryset:
            profile, created = MyProfile.objects.get_or_create(user=user)
            profile.is_approved = False
            profile.save()
        self.message_user(request, f'Снято одобрение с пользователей: {queryset.count()}')


@admin.register(UserLoginStats)
class UserLoginStatsAdmin(admin.ModelAdmin):
    """Административный интерфейс для статистики входов пользователей."""

    list_display = ('user', 'login_date', 'login_count',
                    'first_login_at', 'last_login_at')
    list_filter = ('login_date', 'user__profile__is_approved')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'login_date'
    readonly_fields = ('first_login_at', 'last_login_at')
    ordering = ('-login_date', '-last_login_at')

    # Автодополнение для поля user - выпадающий список с поиском
    autocomplete_fields = ['user']


# Перерегистрируем модель User с кастомным админ-классом
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)