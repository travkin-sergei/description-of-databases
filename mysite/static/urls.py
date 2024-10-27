from django.urls import path
from . import views
from .views import page_note_found

urlpatterns = [
    # столбцы таблиц
    path('', views.defColumnView, name='column'),
    # Таблица данных
    path('table/', views.defTableView, name='table'),
    path('table/<int:table_id>/', views.defTableView_id, name='table_id'),
    # stage
    path('table_stage/', views.defTableView_id_stage, name='table_id_stage'),
    path('table_stage/<int:stage_ig>/', views.defTableView_id_stage_id, name='table_id_stage_id'),
    # базы данных
    path('base/', views.defBasesView, name='base'),
    path('base/<int:base_id>/', views.defBasesView_id, name='base_id'),
    # Функция
    path('function/', views.defFunctionView, name='function'),
    path('function/<int:function_id>/', views.defFunctionView_id, name='function_id'),
    # ссылки столбцов
    path('link/', views.defUpdateView, name='link'),
    path('link/<int:update_id>/', views.defUpdateView_id, name='link_id'),
    # ссылки Сервисы
    path('service/', views.defServiceView, name='service'),
    path('service/<int:service_id>/', views.defServiceView_id, name='service_id'),
]
handler404 = page_note_found
