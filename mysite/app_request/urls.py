from django.urls import path

from .views import (
    AboutView, PageNotFoundView,
    ColumnGroupListView, ColumnGroupDetailView,
)

app_name = "app_request"

urlpatterns = [
    path('', AboutView.as_view(), name='about-app'),
    path('group-name/', ColumnGroupListView.as_view(), name='group_name'),
    path('group-name/<int:pk>/', ColumnGroupDetailView.as_view(), name='group_name-detail'),
]
handler404 = PageNotFoundView.as_view()
