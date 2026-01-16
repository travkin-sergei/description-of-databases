from django.urls import path

from .views.web import (
    AboutView,
    DimUpdateMethodView,
    DimUpdateMethodDetailView,
)
from .apps import name

app_name = name

urlpatterns = [
    # API
    # WEB
    path('about-app/', AboutView.as_view(), name='about-app'),
    path('updates/', DimUpdateMethodView.as_view(), name='updates'),
    path('updates/<int:pk>/', DimUpdateMethodDetailView.as_view(), name='updates-detail'),
]
