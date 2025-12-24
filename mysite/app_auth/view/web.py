# app_auth/web.py
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.views.generic import CreateView, RedirectView, TemplateView
from django.shortcuts import get_object_or_404

from datetime import timedelta
from rest_framework.authtoken.models import Token

from app_auth.models import MyProfile
from ..forms import MyUserCreationForm
from ..models import MyProfile, UserLoginStats


class AboutView(LoginRequiredMixin, TemplateView):
    """Страница о приложении."""

    template_name = 'app_auth/about-application.html'
    title = "О приложении"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


class MyProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'app_auth/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Текущий пользователь
        user = self.request.user

        # Загружаем профиль пользователя
        try:
            profile = user.profile
        except MyProfile.DoesNotExist:
            profile = None
            context['services_roles'] = []
        else:
            # Получаем все записи LinkResponsiblePerson для этого профиля
            responsibilities = profile.linkresponsibleperson_set.select_related(
                'service__type', 'role'
            ).all()

            # Формируем список сервисов и ролей
            services_roles = []
            for resp in responsibilities:
                services_roles.append({
                    'service_alias': resp.service.alias,
                    'service_type': resp.service.type.name,
                    'role_name': resp.role.name,
                })
            context['services_roles'] = services_roles

        context['profile'] = profile
        context['login_stats'] = user.login_stats.order_by('-login_date')
        return context


class MyPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """Изменение пароля пользователя"""

    template_name = 'app_auth/password-change.html'
    success_url = reverse_lazy('app_auth:password_change_done')  # Исправлено на подчёркивания


class MyPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    """Сообщение об успешном изменении пароля"""

    template_name = 'app_auth/password-change-done.html'


class MyLoginView(LoginView):
    template_name = 'app_auth/login.html'

    def form_valid(self, form):
        user = form.get_user()
        if user.is_superuser:
            return super().form_valid(form)
        try:
            profile = user.profile
        except MyProfile.DoesNotExist:
            messages.error(self.request, "Ошибка профиля. Обратитесь к администратору.")
            return self.render_to_response(self.get_context_data(form=form))
        if not profile.is_approved:
            messages.error(self.request, "Ваш аккаунт ещё не одобрен администратором.")
            return self.render_to_response(self.get_context_data(form=form))
        return super().form_valid(form)


class MyRegisterView(CreateView):
    form_class = MyUserCreationForm
    template_name = 'app_auth/register.html'
    success_url = reverse_lazy('app_auth:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Регистрация прошла успешно. Ожидайте одобрения администратора.")
        return response


class MyLogoutView(LogoutView):
    next_page = 'app_auth:login'


class AdminDashboardView(UserPassesTestMixin, TemplateView):
    template_name = 'app_auth/admin_dashboard.html'
    login_url = '/accounts/login/'

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profiles = MyProfile.objects.select_related('user').order_by('-id')
        now = timezone.now()
        today = now.date()
        week_ago = now - timedelta(days=7)

        context.update(
            {
                'profiles': profiles,
                'total': User.objects.count(),
                'approved': profiles.filter(is_approved=True).count(),
                'pending': profiles.filter(is_approved=False).count(),
                'logins_today': UserLoginStats.objects.filter(login_date=today).count(),
                'logins_week': UserLoginStats.objects.filter(login_date__gte=week_ago.date()).count(),
                'tokens': Token.objects.select_related('user'),
            }
        )
        return context


class ApproveUserView(UserPassesTestMixin, RedirectView):
    pattern_name = 'app_auth:admin_dashboard'

    def test_func(self):
        return self.request.user.is_staff

    def get_redirect_url(self, *args, **kwargs):
        profile = get_object_or_404(MyProfile, user_id=kwargs['user_id'])
        profile.is_approved = True
        profile.save()
        messages.success(self.request, f"✅ {profile.user.username} одобрен.")
        return super().get_redirect_url()


class RejectUserView(UserPassesTestMixin, RedirectView):
    pattern_name = 'app_auth:admin_dashboard'

    def test_func(self):
        return self.request.user.is_staff

    def get_redirect_url(self, *args, **kwargs):
        profile = get_object_or_404(MyProfile, user_id=kwargs['user_id'])
        profile.is_approved = False
        profile.save()
        messages.warning(self.request, f"⚠️ {profile.user.username} отклонён.")
        return super().get_redirect_url()


class RegenerateTokenView(UserPassesTestMixin, RedirectView):
    pattern_name = 'app_auth:admin_dashboard'

    def test_func(self):
        return self.request.user.is_staff

    def get_redirect_url(self, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs['user_id'])
        Token.objects.filter(user=user).delete()
        Token.objects.create(user=user)
        messages.info(self.request, f"🔄 Токен для {user.username} обновлён.")
        return super().get_redirect_url()
