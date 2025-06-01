from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from django_filters.views import FilterView

from ..models import Asset
from ..filters import AssetFilter





class AboutAppView(TemplateView):
    """Информационная страница о приложении."""
    template_name = "my_data_asset/about_application.html"
    paginate_by = 20


class AssetDomainView(TemplateView):
    """Страница для отображения доменов данных (пока без логики)."""
    template_name = "my_data_asset/asset_domain.html"
    paginate_by = 20


class AssetView(FilterView):
    """
    Представление для отображения списка источников данных.
    Использует фильтрацию и отображает шаблон.
    """
    model = Asset
    filterset_class = AssetFilter
    template_name = "my_data_asset/asset.html"
    context_object_name = "assets"
    paginate_by = 20  # можно убрать или настроить как нужно


class AssetDetailView(DetailView):
    model = Asset
    template_name = 'my_data_asset/asset-detail.html'  # создашь позже
    context_object_name = 'asset'
    paginate_by = 20