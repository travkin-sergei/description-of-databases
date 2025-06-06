from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .view.views import (
    about_me,
    page_note_found,
    BasesView, BasesViewId,
    FunctionView, FunctionViewId,
    TableView, TableDetailView,
    TableViewIdStage, TableViewIdStageId,
    ColumnView,
    ServiceView,
    UpdateView, UpdateViewId,
    ServiceViewId,
)
from .view.v1 import (
    BaseGroupAPIViewSet,
    BaseAPIViewSet,
    SchemaAPIViewSet,
    TableAPIViewSet,
    TableDetailAPIView,
)

app_name = "my_dba"

routers = DefaultRouter()
routers.register("base_group", BaseGroupAPIViewSet)
routers.register("base", BaseAPIViewSet)
routers.register("schema", SchemaAPIViewSet)
routers.register("table", TableAPIViewSet)

urlpatterns = [
    path('about-me/', about_me, name='about-app'),
    # start ------- подключение API
    path("v1/api/", include(routers.urls)),
    path("v1/api/tab_id/<int:pk>/", TableDetailAPIView.as_view()),
    # stop  ------- подключение API
    # базы данных
    path('base/', BasesView.as_view(), name='base'),
    path('base/<int:pk>/', BasesViewId.as_view(), name='base_id'),
    # столбцы таблиц
    path('', ColumnView.as_view(), name='column'),
    # Таблица данных
    path('table/', TableView.as_view(), name='table'),
    path('table/<int:pk>/', TableDetailView.as_view(), name='table_id'),
    # stage
    path('table_stage/', TableViewIdStage.as_view(), name='table_id_stage'),
    path('table_stage/<int:pk>/', TableViewIdStageId.as_view(), name='table_id_stage_id'),
    # Функция
    path('function/', FunctionView.as_view(), name='function'),
    path('function/<int:pk>/', FunctionViewId.as_view(), name='function_id'),
    # ссылки столбцов
    path('my_update/', UpdateView.as_view(), name='my_update'),
    path('link/<int:pk>/', UpdateViewId.as_view(), name='link_id'),
    # ссылки Сервисы
    path('service/', ServiceView.as_view(), name='service'),
    path('service/<int:pk>/', ServiceViewId.as_view(), name='service_id'),
    # Регистрация
]
handler404 = page_note_found
