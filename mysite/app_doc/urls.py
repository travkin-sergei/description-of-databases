from mysite.app_doc.views.web import (
    PageNotFoundView, AboutView,
)
from django.urls import path
from .apps import app

app_name = app

urlpatterns = [
    # API
    # WEB
    path('about-app/', AboutView.as_view(), name='about-app'),
]
handler404 = PageNotFoundView.as_view()
