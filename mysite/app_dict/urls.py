from .views.web import (
    PageNotFoundView, AboutView,
    DictionaryView, DictionaryDetailView,
)
from django.urls import path
from .apps import name

app_name = name

urlpatterns = [
    # API
    # WEB
    path('about-app/', AboutView.as_view(), name='about-app'),
    path('dict/', DictionaryView.as_view(), name='dictionary'),
    path('dict-detail/<int:pk>', DictionaryDetailView.as_view(), name='dictionary-detail'),
]
handler404 = PageNotFoundView.as_view()
