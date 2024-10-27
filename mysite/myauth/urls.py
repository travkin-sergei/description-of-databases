from django.contrib.auth.views import LoginView
from django.urls import path


from .view.views import MyLogoutView
app_name = "myauth"

urlpatterns = [
    path('login/', LoginView.as_view(template_name="myauth/login.html", redirect_authenticated_user=True),name='login'),
    path('logout/', MyLogoutView.as_view(), name='logout'),
]
