from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy


class MyLogoutView(LogoutView):
    next_page = reverse_lazy("myauth:login")
