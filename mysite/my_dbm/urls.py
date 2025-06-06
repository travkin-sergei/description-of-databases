from django.urls import path, include

from .views.web import (
    PageNotFoundView, AboutView,
    TablesView, DatabasesView, TableDetailView, DatabaseDetailView,
)

app_name = "my_dbm"

urlpatterns = [
    path('', AboutView.as_view(), name='about-app'),
    path('databases/', DatabasesView.as_view(), name='databases'),
    path('databases/<int:pk>/', DatabaseDetailView.as_view(), name='databases-detail'),
    path('tables/', TablesView.as_view(), name='tables'),
    path('tables/<int:pk>/', TableDetailView.as_view(), name='tables-detail'),

]
handler404 = PageNotFoundView.as_view()
