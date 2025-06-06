from django.urls import path

from .views import (
    AboutView,
    PageNotFoundView,
    LinkColumnUpdateView,
)

app_name = "my_updates"

urlpatterns = [
    path('about-app/', AboutView.as_view(), name='about-app'),
    path('updates/', LinkColumnUpdateView.as_view(), name='updates'),
    # path('updates-detail/', LinkColumnUpdateListView.as_view(), name='updates-detail'),
]
handler404 = PageNotFoundView.as_view()
