from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView, CreateView
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from my_services.models import LinkResponsiblePerson
from .models import MyProfile


class MyPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """Изменение пароля пользователя"""

    template_name = 'my_auth/password-change.html'
    success_url = reverse_lazy('my_auth:password_change_done')  # Исправлено на подчёркивания


class AboutAppView(TemplateView):
    """Информационная страница о приложении."""

    template_name = "my_auth/about-application.html"


class MyPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    """Сообщение об успешном изменении пароля"""

    template_name = 'my_auth/password-change-done.html'


class MyProfileView(LoginRequiredMixin, DetailView):
    """Просмотр профиля пользователя с сервисами и ролями"""
    model = MyProfile
    template_name = 'my_auth/profile.html'
    context_object_name = 'profile'

    def get_object(self):
        # Получаем или создаем профиль, если его нет
        profile, created = MyProfile.objects.get_or_create(user=self.request.user)
        if created:
            messages.info(self.request, "Профиль был автоматически создан")
        return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        # Получаем все сервисы, где участвует текущий пользователь
        context['responsibilities'] = (
            LinkResponsiblePerson.objects
            .select_related("service", "role")
            .filter(name=profile)
            .order_by("service__alias")
        )
        return context


class MyLoginView(LoginView):
    """Идентификация пользователя."""

    template_name = 'my_auth/login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('my_dbm:tables')  # После входа в аккаунт перенаправление в приложение my_dba

    def form_invalid(self, form):
        messages.error(self.request, 'Неверное имя пользователя или пароль')
        return super().form_invalid(form)


class MyRegisterView(CreateView):
    """Регистрация пользователя."""

    form_class = UserCreationForm  # Стандартная форма регистрации Django
    template_name = 'my_auth/register.html'  # Путь к шаблону
    success_url = reverse_lazy('my_auth:login')  # Перенаправление после успешной регистрации

    def form_valid(self, form):
        # Сохраняем пользователя
        response = super().form_valid(form)

        # Автоматически входим после регистрации
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(self.request, user)
            messages.success(self.request, 'Регистрация прошла успешно!')
        else:
            messages.error(self.request, 'Ошибка входа после регистрации')

        return response


class MyLogoutView(LogoutView):
    """Выход из профиля"""

    next_page = reverse_lazy("my_auth:login")