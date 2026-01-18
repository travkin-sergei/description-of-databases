from .views import (
    PageNotFoundView, AboutView,
    DictionaryView, DictionaryDetailView,
)
from django.urls import path

app_name = "app_dictionary"

urlpatterns = [
    path('', AboutView.as_view(), name='about-app'),
    path('dictionary/', DictionaryView.as_view(), name='dictionary'),
    path('dictionary-detail/<int:pk>', DictionaryDetailView.as_view(), name='dictionary-detail'),

]
handler404 = PageNotFoundView.as_view()