# app_auth/urls.py
from django.urls import path

from .apps import AppAuthConfig
from .view.v1 import RegisterRequestView, ProfileDetailView
from .view.web import (
    AboutView, DimProfileView,
    MyLoginView,
    MyLogoutView,
    MyRegisterView,
    MyPasswordChangeView,
    MyPasswordChangeDoneView,
    AdminDashboardView,
    ApproveRequestView,
    RejectRequestView,
    CreateUserManuallyView,
)

app_name = AppAuthConfig.name

urlpatterns = [
    # API
    path('register/', RegisterRequestView.as_view(), name='api_register'),
    path('profile/', ProfileDetailView.as_view(), name='api_profile'),
    # web
    path('', DimProfileView.as_view(), name='profile'),
    path('about-app/', AboutView.as_view(), name='about-app'),
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', MyLogoutView.as_view(), name='logout'),
    path('register/', MyRegisterView.as_view(), name='register'),
    path('password-change/', MyPasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', MyPasswordChangeDoneView.as_view(), name='password_change_done'),
    # Админка
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin-approve/<int:request_id>/', ApproveRequestView.as_view(), name='approve_request'),
    path('admin-reject/<int:request_id>/', RejectRequestView.as_view(), name='reject_request'),
    path('admin-create-user/', CreateUserManuallyView.as_view(), name='create_user_manually'),
]
