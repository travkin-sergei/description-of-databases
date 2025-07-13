from django.urls import path, include

from .views import (
    AboutView, PageNotFoundView,
    ListOfReferencesView,
)

app_name = "my_external_sources"

urlpatterns = [
    path('', AboutView.as_view(), name='about-app'),
    path('ListOfReferences/', ListOfReferencesView.as_view(), name='List-References'),
]
handler404 = PageNotFoundView.as_view()
