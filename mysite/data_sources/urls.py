from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .view.v1 import (
    DataSourcesAPIViewSet,
)
from .view.views import (
    DataSourcesView, about_me,
)

app_name = "data_sources"

routers = DefaultRouter()
routers.register("list", DataSourcesAPIViewSet)

urlpatterns = [
    path('about-me/', about_me, name='about_me'),
    path("v1/api/", include(routers.urls)),
    path('', DataSourcesView.as_view(), name='data-sources'),
]
