from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('summernote/', include('django_summernote.urls')),  # настройка редактора в админке
    path('admin/doc/', include('django.contrib.admindocs.urls')),  # Документация
    path('admin/', admin.site.urls),

    # Общая схема и документация
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),  # Открытая схема API
    path('api/schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),  # Swagger
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),  # ReDoc

    # Приложения
    path('', include('my_dbm.urls')),
    path('accounts/', include('my_auth.urls', namespace='my_auth')),
    path('dictionary/', include('my_dictionary.urls')),
    path('services/', include('my_services.urls')),
    path('request/', include('my_request.urls')),
    path('updates/', include('my_updates.urls')),
    path('query/', include('my_query_path.urls')),

]

if settings.DEBUG:
    urlpatterns.extend(
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )
    urlpatterns.extend(
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    )
