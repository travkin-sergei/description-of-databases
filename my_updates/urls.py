from django.urls import path

from .views import (
    AboutView,
    PageNotFoundView,
    DimUpdateMethodView,
    DimUpdateMethodDetailView,
)

app_name = "my_updates"

urlpatterns = [
    path('about-app/', AboutView.as_view(), name='about-app'),
    path('updates/', DimUpdateMethodView.as_view(), name='updates'),
    path('updates/<int:pk>/', DimUpdateMethodDetailView.as_view(), name='updates-detail'),
]
handler404 = PageNotFoundView.as_view()
