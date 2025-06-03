from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.shortcuts import render
def about_me(request):
    """
    Отображение информации о текущем приложении из шалона.
    """
    return render(request, 'my_auth/about-application.html')
class MyLogoutView(LogoutView):
    next_page = reverse_lazy("my_auth:login")
