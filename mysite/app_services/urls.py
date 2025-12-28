from django.urls import path

from .views import (
    PageNotFoundView, AboutView,
    ServicesView, ServicesDetailView,
    DimLinkListView,
    ServiceUserView,
)

app_name = "app_services"

urlpatterns = [
    path('about-app/', AboutView.as_view(), name='about-app'),
    path('services/', ServicesView.as_view(), name='services'),
    path('services/<int:pk>/', ServicesDetailView.as_view(), name='services-detail'),
    path('services-user/', ServiceUserView.as_view(), name='services-user'),
    path('link/', DimLinkListView.as_view(), name='dim-link'),

]
handler404 = PageNotFoundView.as_view()
