# app_auth/view/web.py
"""
Представления (views) для модуля аутентификации и управления профилями пользователей.

Содержит:
- Регистрацию, вход, выход, смену пароля.
- Профиль пользователя с возможностью редактирования и просмотром статистики входов.
- Административные представления: панель, одобрение/отклонение, управление.

Все представления используют кастомную модель MyProfile (AbstractUser).
"""
import secrets
from typing import Any, Dict, Optional
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView, View, DetailView
from django.db.models import Sum, Min, Max
from django.http import HttpRequest, HttpResponse

# Импорт форм и моделей из текущего приложения
from ..forms import MyUserLoginForm, MyUserRegisterForm, MyProfileForm
from ..models import MyProfile, LoginStat  # ← явный импорт для аннотаций


# === Основные представления пользователя ===

class MyRegisterView(CreateView):
    """
    Представление регистрации нового пользователя.

    Использует кастомную форму MyUserRegisterForm.
    После успешной регистрации — перенаправление на страницу входа.
    """
    model = MyProfile
    form_class = MyUserRegisterForm
    template_name = 'app_auth/register.html'
    success_url = reverse_lazy('app_auth:login')

    def form_valid(self, form: MyUserRegisterForm) -> HttpResponse:
        """
        Обработка валидной формы регистрации.

        Args:
            form: Валидная форма регистрации.

        Returns:
            HttpResponse: Перенаправление на success_url.
        """
        response = super().form_valid(form)
        messages.success(self.request, 'Регистрация успешна! Теперь вы можете войти.')
        return response


class MyLoginView(LoginView):
    """
    Представление входа в систему.

    Использует кастомную форму MyUserLoginForm.
    Авторизованным пользователям запрещён повторный вход (redirect_authenticated_user=True).
    После входа — перенаправление в профиль.
    """

    form_class = MyUserLoginForm
    template_name = 'app_auth/login.html'
    redirect_authenticated_user = True

    def get_success_url(self) -> str:
        """Возвращает URL профиля после успешного входа."""
        return reverse_lazy('app_auth:profile')


class MyLogoutView(LogoutView):
    """
    Представление выхода из системы.

    После выхода — перенаправление на страницу входа.
    Показывает информационное сообщение.
    """
    next_page = reverse_lazy('app_auth:login')

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Перехват запроса на выход для показа сообщения.

        Args:
            request: Текущий HTTP-запрос.

        Returns:
            HttpResponse: Результат вызова родительского метода.
        """
        messages.info(request, 'Вы успешно вышли из системы.')
        return super().dispatch(request, *args, **kwargs)


# === Представления для смены пароля ===

class MyPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """
    Представление смены пароля для авторизованных пользователей.

    После успешной смены — перенаправление на страницу подтверждения.
    """
    template_name = 'app_auth/password-change.html'
    success_url = reverse_lazy('app_auth:password_change_done')

    def form_valid(self, form: MyUserRegisterForm) -> HttpResponse:
        """Добавляет success-сообщение после смены пароля."""
        messages.success(self.request, 'Пароль успешно изменен!')
        return super().form_valid(form)


class MyPasswordChangeDoneView(LoginRequiredMixin, TemplateView):
    """
    Страница подтверждения успешной смены пароля.
    """
    template_name = 'app_auth/password-change-done.html'


# === Миксин для административных представлений ===

class IsStaffMixin(UserPassesTestMixin):
    """
    Миксин для проверки прав доступа к административным разделам.

    Доступ разрешён только staff или superuser.
    При отказе — перенаправление на вход с ошибкой.
    """

    def test_func(self) -> bool:
        """Проверяет, имеет ли пользователь права администратора."""
        return self.request.user.is_staff or self.request.user.is_superuser

    def handle_no_permission(self) -> HttpResponse:
        """Показывает сообщение и перенаправляет при отсутствии прав."""
        messages.error(self.request, 'У вас нет прав для доступа к этой странице.')
        return redirect('app_auth:login')


# === Административные представления ===

class AdminDashboardView(LoginRequiredMixin, IsStaffMixin, TemplateView):
    """
    Главная административная панель.

    Отображает список пользователей (кроме суперпользователей).
    """
    template_name = 'app_auth/admin_dashboard.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Добавляет в контекст список пользователей.

        Returns:
            Словарь контекста с ключом 'users'.
        """
        context = super().get_context_data(**kwargs)
        context['users'] = MyProfile.objects.exclude(is_superuser=True).order_by('-date_joined')
        return context


class ApproveUserView(LoginRequiredMixin, IsStaffMixin, View):
    """
    Обработка POST-запроса на одобрение пользователя (активация аккаунта).
    """

    def post(self, request: HttpRequest, user_id: int) -> HttpResponse:
        """
        Активирует указанного пользователя.

        Args:
            request: HTTP-запрос.
            user_id: ID пользователя.

        Returns:
            Перенаправление на админ-панель.
        """
        user = get_object_or_404(MyProfile, id=user_id)
        user.is_active = True
        user.save(update_fields=['is_active'])
        messages.success(request, f'Пользователь {user.username} одобрен и активирован.')
        return redirect('app_auth:admin_dashboard')


class RejectUserView(LoginRequiredMixin, IsStaffMixin, View):
    """
    Обработка POST-запроса на отклонение пользователя (деактивация).
    """

    def post(self, request: HttpRequest, user_id: int) -> HttpResponse:
        """Деактивирует пользователя и перенаправляет."""
        user = get_object_or_404(MyProfile, id=user_id)
        user.is_active = False
        user.save(update_fields=['is_active'])
        messages.warning(request, f'Пользователь {user.username} отклонен и деактивирован.')
        return redirect('app_auth:admin_dashboard')


class RegenerateTokenView(LoginRequiredMixin, IsStaffMixin, View):
    """
    Генерация нового токена для пользователя (пример — для API или 2FA).

    ⚠️ В текущей реализации токен НЕ сохраняется в БД — только показывается.
    Для продакшена нужно добавить поле в модель и сохранение.
    """

    def post(self, request: HttpRequest, user_id: int) -> HttpResponse:
        """Генерирует и показывает временный токен."""
        user = get_object_or_404(MyProfile, id=user_id)
        new_token = secrets.token_hex(16)  # 32-символьный hex-токен
        # TODO: сохранить в user.auth_token и вызвать user.save()
        messages.info(request, f'Для пользователя {user.username} сгенерирован новый токен: {new_token}')
        return redirect('app_auth:admin_dashboard')


# === Прочие представления ===

class AboutView(TemplateView):
    """
    Статическая страница "О приложении".
    """
    template_name = 'app_auth/about-application.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Добавляет заголовок страницы в контекст."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'О приложении'
        return context


class UserManagementView(LoginRequiredMixin, IsStaffMixin, TemplateView):
    """
    Страница управления пользователями: одобренные и ожидающие.
    """
    template_name = 'app_auth/user_management.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Формирует списки пользователей для отображения."""
        context = super().get_context_data(**kwargs)
        context['pending_users'] = MyProfile.objects.filter(is_active=False)
        context['active_users'] = MyProfile.objects.filter(is_active=True)
        return context


# === Профиль пользователя с редактированием и статистикой входов ===

class MyProfileView(LoginRequiredMixin, UpdateView):
    """
    Представление профиля пользователя.

    Позволяет:
    - редактировать профиль (first_name, last_name, email, gender, link_profile)
    - просматривать статистику входов за последние 30 дней
    - видеть общую статистику: всего входов, первый/последний вход

    Использует кастомную форму MyProfileForm.
    Данные статистики берутся из модели LoginStat (связанной через related_name='login_stats').
    """
    model = MyProfile
    form_class = MyProfileForm
    template_name = 'app_auth/profile.html'
    context_object_name = 'user'

    def get_object(self, queryset: Optional[Any] = None) -> MyProfile:
        """
        Возвращает текущего авторизованного пользователя.

        Overrides:
            UpdateView.get_object — чтобы редактировать только свой профиль.
        """
        return self.request.user

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Добавляет в контекст:
        - login_stats: последние 30 записей статистики входов
        - total_logins: общее число входов
        - first_ever: дата и время первого входа вообще
        - last_ever: дата и время последнего входа вообще

        Если статистика ещё не создана — значения будут None/0.
        """
        context = super().get_context_data(**kwargs)

        # Получаем последние 30 дней входов (уже отсортировано в представлении)
        context['login_stats'] = (
            self.request.user.login_stats
            .select_related()  # оптимизация: избегаем N+1
            .order_by('-login_date')[:30]
        )

        # Агрегация общей статистики
        stats_agg = self.request.user.login_stats.aggregate(
            total_logins=Sum('login_count'),
            first_ever=Min('first_login_at'),
            last_ever=Max('last_login_at'),
        )

        # Устанавливаем значения по умолчанию, если нет записей
        context['total_logins'] = stats_agg['total_logins'] or 0
        context['first_ever'] = stats_agg['first_ever']
        context['last_ever'] = stats_agg['last_ever']

        return context

    def form_valid(self, form: MyProfileForm) -> HttpResponse:
        """Добавляет success-сообщение при успешном обновлении профиля."""
        messages.success(self.request, 'Ваш профиль успешно обновлён.')
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """После сохранения — остаёмся на странице профиля."""
        return reverse_lazy('app_auth:profile')
