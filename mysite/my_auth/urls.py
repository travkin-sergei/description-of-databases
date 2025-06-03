from django.contrib.auth.views import LoginView
from django.urls import path

from .view.views import (
    about_me,
    MyLogoutView,
)

app_name = "my_auth"

urlpatterns = [
    path('about-me/', about_me, name='about_me'),
    path('login/',
         LoginView.as_view(template_name="my_auth/login.html", redirect_authenticated_user=True), name='login'
         ),
    path('logout/', MyLogoutView.as_view(), name='logout'),
]
