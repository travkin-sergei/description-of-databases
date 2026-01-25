# app_doc/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.v1 import DimDocTypeViewSet, DimDocViewSet

app_name = 'app_doc'

router = DefaultRouter()
router.register(r'doc-types', DimDocTypeViewSet, basename='doc-type')
router.register(r'docs', DimDocViewSet, basename='doc')

urlpatterns = [
    path('api/v1/', include(router.urls)),
]