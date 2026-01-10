# app_url/urls.py
from django.urls import path

from .views.web import (
    AboutView, PageNotFoundView,
    DimLinListView, DimLinDetailView,
)

from .apps import name

app_name = name

urlpatterns = [
    # API
    # WEB
    path('about-app/', AboutView.as_view(), name='about-app'),
    path('', DimLinListView.as_view(), name='dimlin_list'),
    path('link/<int:pk>/', DimLinDetailView.as_view(), name='dimlin_detail'),
]
handler404 = PageNotFoundView.as_view()
