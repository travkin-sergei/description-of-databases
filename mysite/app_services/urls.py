# app_services/urls.py
from django.urls import path
from .views.web import (
    PageNotFoundView, AboutView,
    ServicesView, ServicesDetailView,
    LinksUrlServiceListView,  # Изменено: DimLinkListView -> LinksUrlServiceListView
    ServiceUserView,
)
from .apps import name

app_name = name

urlpatterns = [
    # API
    # WEB
    path('about-app/', AboutView.as_view(), name='about-app'),
    path('services/', ServicesView.as_view(), name='services'),
    path('services/<int:pk>/', ServicesDetailView.as_view(), name='services-detail'),
    path('services-user/', ServiceUserView.as_view(), name='services-user'),
    path('link/', LinksUrlServiceListView.as_view(), name='dim-link'),  # Изменено здесь тоже

]
handler404 = PageNotFoundView.as_view()
