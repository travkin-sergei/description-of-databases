from django.urls import path

from .views import (
    PageNotFoundView, AboutView,
    ServicesView, ServicesDetailView,
)

app_name = "my_services"

urlpatterns = [
    path('services/', ServicesView.as_view(), name='services'),
    path('services/<int:pk>/', ServicesDetailView.as_view(), name='services-detail'),
    path('about-app/', AboutView.as_view(), name='about-app'),
]
handler404 = PageNotFoundView.as_view()
