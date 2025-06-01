from django.urls import path, include
from rest_framework.routers import DefaultRouter

#from .view.v1 import DataAssetAPIViewSet
from .view.web import (
    AboutAppView,
    AssetView,
    # AssetDomainView,
    # AssetDetailView,
)

app_name = 'my_data_asset'
router = DefaultRouter()
#router.register("assets", DataAssetAPIViewSet)

urlpatterns = [
    # API
    path('v1/api/', include(router.urls)),
    # WEB
    path('', AboutAppView.as_view(), name='about-app'),
    # Источники данных
    path('assets/', AssetView.as_view(), name='data-asset'),
    # path('assets/<int:pk>/', AssetDetailView.as_view(), name='data-asset-detail'),
    # # Источники данных dddx
    # path('asset/asset/', AssetDomainView.as_view(), name='asset-domain'),

]
