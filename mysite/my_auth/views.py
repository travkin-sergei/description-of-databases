from datetime import timedelta
from .utils import count_authenticated_sessions

from django.http import HttpResponseNotFound
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views import View
from django.views.generic import DetailView, TemplateView, CreateView
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordChangeDoneView
)
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import MyProfile


class PageNotFoundView(View):
    """Обработка 404 ошибки отсутствия страницы"""

    def get(self, request, *args, **kwargs):
        return HttpResponseNotFound("<h1>Страница не найдена 404 ошибка</h1>")


class AboutView(TemplateView):
    """Страница о приложении."""

    template_name = 'my_dbm/about-application.html'
    title = "О приложении"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


class MyPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'my_auth/password-change.html'
    success_url = reverse_lazy('my_auth:password_change_done')


class MyPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = 'my_auth/password-change-done.html'


class MyProfileView(LoginRequiredMixin, DetailView):
    model = MyProfile
    template_name = 'my_auth/profile.html'
    context_object_name = 'profile'

    def get_object(self):
        profile, created = MyProfile.objects.get_or_create(user=self.request.user)
        if created:
            messages.info(self.request, "Профиль был автоматически создан")
        return profile


class AboutAppView(TemplateView):
    template_name = "my_auth/about-application.html"


class MyLoginView(LoginView):
    template_name = 'my_auth/login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('my_auth:profile')

    def form_invalid(self, form):
        messages.error(self.request, 'Неверное имя пользователя или пароль')
        return super().form_invalid(form)


class MyRegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'my_auth/register.html'
    success_url = reverse_lazy('my_auth:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)

        if user:
            login(self.request, user)
            messages.success(self.request, 'Регистрация прошла успешно!')
            # Создаем профиль при регистрации
            MyProfile.objects.get_or_create(user=user)
        else:
            messages.error(self.request, 'Ошибка входа после регистрации')

        return response


class MyLogoutView(LogoutView):
    next_page = reverse_lazy("my_auth:login")

    from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def user_stats_view(request):
    context = {
        'total_users': User.objects.count(),
        'logged_in_today': User.objects.filter(
            last_login__gte=now() - timedelta(days=1)
        )
    }
    return render(request, 'my_auth/stats.html', context)


def dashboard_view(request):
    active_users_count = count_authenticated_sessions()
    return render(request, 'my_auth/dashboard.html', {
        'active_users_count': active_users_count
    })
