# app_auth/urls.py
from django.urls import path

from .models import db_schema
from .view.web import (
    MyLoginView, MyRegisterView, MyLogoutView,
    AdminDashboardView, ApproveUserView, RejectUserView, RegenerateTokenView, MyProfileView, AboutView,
    MyPasswordChangeView, MyPasswordChangeDoneView,
)

app_name = db_schema

urlpatterns = [
    path('', AboutView.as_view(), name='about-app'),
    # Пароли
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', MyLogoutView.as_view(), name='logout'),
    path('register/', MyRegisterView.as_view(), name='register'),
    path('profile/', MyProfileView.as_view(), name='profile'),
    # Пароли
    path('password-change/', MyPasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', MyPasswordChangeDoneView.as_view(), name='password_change_done'),

    # Админпанель — всё на одной странице
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin-approve/<int:user_id>/', ApproveUserView.as_view(), name='approve_user'),
    path('admin-reject/<int:user_id>/', RejectUserView.as_view(), name='reject_user'),
    path('admin-token/<int:user_id>/', RegenerateTokenView.as_view(), name='regenerate_token'),

]
