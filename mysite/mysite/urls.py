from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Панель администратора
    path('admin/doc/', include('django.contrib.admindocs.urls')),  # Документация
    path('admin/', admin.site.urls),
    path('summernote/', include('django_summernote.urls')),  # настройка редактора в админке
    # Общая схема и документация
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # Мои приложения
    path('', include('my_dbm.urls')),
    path('account/', include('my_auth.urls')),
    path('services/', include('my_services.urls')),
    path('ExtSources/', include('my_external_sources.urls')),
    path('request/', include('my_request.urls')),
    path('updates/', include('my_updates.urls')),
]
