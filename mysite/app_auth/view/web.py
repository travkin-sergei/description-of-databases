from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import CreateView, TemplateView, UpdateView, View
from django.urls import reverse_lazy
from django.utils import timezone

from ..forms import (
    RegistrationRequestForm,
    MyUserLoginForm,
    MyProfileForm,
    ManualUserCreationForm
)
from ..models import MyProfile, RegistrationRequest


class AboutView(TemplateView):
    template_name = 'app_auth/about.html'


class MyLoginView(LoginView):
    template_name = 'app_auth/login.html'
    form_class = MyUserLoginForm


class MyRegisterView(CreateView):
    """Оставить заявку на регистрацию"""
    model = RegistrationRequest
    form_class = RegistrationRequestForm
    template_name = 'app_auth/register.html'
    success_url = reverse_lazy('app_auth:login')

    def form_valid(self, form):
        messages.success(
            self.request,
            'Заявка отправлена. Администратор создаст вам аккаунт и отправит данные на email.'
        )
        return super().form_valid(form)


class MyLogoutView(LogoutView):
    next_page = reverse_lazy('app_auth:login')


class MyProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'app_auth/profile.html'
    form_class = MyProfileForm
    success_url = reverse_lazy('app_auth:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Профиль обновлен')
        return super().form_valid(form)


class MyPasswordChangeView(PasswordChangeView):
    template_name = 'app_auth/password-change.html'
    success_url = reverse_lazy('app_auth:password-change_done')


class MyPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'app_auth/password_change_done.html'


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class AdminDashboardView(AdminRequiredMixin, TemplateView):
    """Админка: просмотр заявок и создание пользователей"""
    template_name = 'app_auth/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_requests'] = RegistrationRequest.objects.filter(
            status='pending'
        ).order_by('-created_at')
        context['create_user_form'] = ManualUserCreationForm()
        return context


class ApproveRequestView(AdminRequiredMixin, View):
    """Одобрить заявку (просто пометить как одобренную)"""

    def post(self, request, request_id):
        registration_request = get_object_or_404(
            RegistrationRequest,
            id=request_id,
            status='pending'
        )
        registration_request.status = 'approved'
        registration_request.save()
        messages.success(request, f'Заявка от {registration_request.email} одобрена')
        return redirect('app_auth:admin_dashboard')


class RejectRequestView(AdminRequiredMixin, View):
    """Отклонить заявку"""

    def post(self, request, request_id):
        registration_request = get_object_or_404(
            RegistrationRequest,
            id=request_id,
            status='pending'
        )
        registration_request.status = 'rejected'
        registration_request.save()
        messages.success(request, f'Заявка от {registration_request.email} отклонена')
        return redirect('app_auth:admin_dashboard')


class CreateUserManuallyView(AdminRequiredMixin, View):
    """Администратор создает пользователя вручную"""

    def post(self, request):
        form = ManualUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f'Пользователь {user.username} создан. '
                f'Отправьте ему логин и пароль: {form.cleaned_data["password1"]}'
            )
        else:
            messages.error(request, 'Ошибка создания пользователя')
        return redirect('app_auth:admin_dashboard')
