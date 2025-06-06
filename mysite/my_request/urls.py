from django.urls import path

from .views import (
    AboutView, PageNotFoundView,
    FZListView,
)

app_name = "my_request"

urlpatterns = [
    path('', AboutView.as_view(), name='about-app'),
    path('fz/', FZListView.as_view(), name='fz-list'),
]
handler404 = PageNotFoundView.as_view()
