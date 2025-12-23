from django.urls import path

from .views import (
    AboutView, PageNotFoundView,
    FZListView, FZDetailView,
)

app_name = "app_request"

urlpatterns = [
    path('', AboutView.as_view(), name='about-app'),
    path('fz/', FZListView.as_view(), name='fz'),
    path('fz/<int:pk>/', FZDetailView.as_view(), name='fz-detail'),
]
handler404 = PageNotFoundView.as_view()
