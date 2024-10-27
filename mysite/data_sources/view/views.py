from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import ListView

from ..filters import DataSourcesFilter
from ..models import DataSources



class DataSourcesView(LoginRequiredMixin,ListView):
    """
    Отображение списка источников данных
    """
    template_name = 'data_sources/DataSourcesView.html'
    model = DataSources
    filter_class = DataSourcesFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filter_class(self.request.GET, queryset=self.model.objects.all())
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        filter = self.filter_class(self.request.GET, queryset=queryset)
        return filter.qs