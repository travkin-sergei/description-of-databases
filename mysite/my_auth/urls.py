from django.urls import path
from .views import (
    AboutAppView, PageNotFoundView,
    MyLoginView,
    MyRegisterView,
    MyLogoutView, MyProfileView, MyPasswordChangeView, MyPasswordChangeDoneView,
    user_stats_view,
    dashboard_view,
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
    path('stats/', user_stats_view, name='user_stats'),
    path('dashboard/', dashboard_view, name='dashboard'),
]
handler404 = PageNotFoundView.as_view()
