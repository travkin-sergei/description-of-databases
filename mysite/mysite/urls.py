from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/doc/', include('django.contrib.admindocs.urls')),  # Документация
    path('admin/', admin.site.urls),
    path('summernote/', include('django_summernote.urls')),  # настройка редактора в админке

    # Общая схема и документация
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),  # Открытая схема API
    path('api/schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),  # Swagger
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),  # ReDoc

    # Приложения
    path('', include('dba.urls')),
    path('accounts/', include('myauth.urls')),
    path('asset/', include('my_data_asset.urls')),

]

if settings.DEBUG:
    urlpatterns.extend(
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )
    urlpatterns.extend(
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    )
