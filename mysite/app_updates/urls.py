from django.urls import path

from .views.web import (
    AboutView,
    PageNotFoundView,
    DimUpdateMethodView,
    DimUpdateMethodDetailView,
)
from .apps import app

app_name = app

urlpatterns = [
    # API
    # WEB
    path('about-app/', AboutView.as_view(), name='about-app'),
    path('updates/', DimUpdateMethodView.as_view(), name='updates'),
    path('updates/<int:pk>/', DimUpdateMethodDetailView.as_view(), name='updates-detail'),
]
handler404 = PageNotFoundView.as_view()
