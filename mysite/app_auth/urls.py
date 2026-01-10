from django.urls import path

from .apps import name
from .view.web import (
    MyLoginView, MyRegisterView, MyLogoutView,
    AdminDashboardView, ApproveRequestView, RejectRequestView,
    CreateUserManuallyView, MyProfileView, AboutView,
    MyPasswordChangeView, MyPasswordChangeDoneView,
)

app_name = name

urlpatterns = [
    # API
    # WEB
    path('', MyProfileView.as_view(), name='profile'),
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
