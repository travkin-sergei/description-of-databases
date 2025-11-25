
from django.urls import path
from .views import (
    AboutAppView,
    MyLoginView,
    MyRegisterView,
    MyLogoutView, MyProfileView, MyPasswordChangeView, MyPasswordChangeDoneView,
)

app_name = 'my_auth'

urlpatterns = [
    path('', AboutAppView.as_view(), name='about-app'),
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', MyLogoutView.as_view(), name='logout'),
    path('register/', MyRegisterView.as_view(), name='register'),
    path('profile/', MyProfileView.as_view(), name='profile'),
    path('password-change/', MyPasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', MyPasswordChangeDoneView.as_view(), name='password_change_done'),
]
