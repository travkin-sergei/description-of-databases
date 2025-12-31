from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('summernote/', include('django_summernote.urls')),  # настройка редактора в админке
    path('admin/doc/', include('django.contrib.admindocs.urls')),  # Документация
    path('admin/', admin.site.urls),
    #
    # Общая схема и документация
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),  # Открытая схема API
    path('api/schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),  # Swagge
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),  # ReDoc

    # Приложения
    path('', include('app_dbm.urls')),
    path('accounts/', include('app_auth.urls', namespace='app_auth')),
    path('dictionary/', include('app_dict.urls')),
    path('services/', include('app_services.urls')),
    path('request/', include('app_request.urls')),
    path('updates/', include('app_updates.urls')),
    path('query/', include('app_query_path.urls')),
    path('link/', include('app_url.urls')),
]

if settings.DEBUG:
    urlpatterns.extend(
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )
    urlpatterns.extend(
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    )
