# mysite/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    # AutoDoc & Admin
    path('summernote/', include('django_summernote.urls')),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    # OpenAPI / Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Веб-часть приложений
    path('', include('app_dbm.urls')),  # Корень — таблицы
    path('accounts/', include('app_auth.urls')),  # Веб-авторизация
    path('doc/', include('app_doc.urls')),
    path('dictionary/', include('app_dict.urls')),
    path('services/', include('app_services.urls')),
    path('request/', include('app_request.urls')),
    path('updates/', include('app_updates.urls')),
    path('query/', include('app_query_path.urls')),
    path('link/', include('app_url.urls')),
]

# Обработчик 404
handler404 = '_common.views.handler404'

# Статика и медиа (только в DEBUG)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
