from mysite.app_doc.views.web import (
    PageNotFoundView, AboutView,
)
from django.urls import path
from .apps import name

app_name = name

urlpatterns = [
    # API
    # WEB
    path('about-app/', AboutView.as_view(), name='about-app'),
]
handler404 = PageNotFoundView.as_view()
