# app_services/filters.py
import django_filters
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django_filters.views import FilterView

from app_auth.models import DimProfile
from app_dbm.models import DimStage

from .models import (
    DimServices,
    DimServicesTypes,
    DimRoles,
    DimTechStack,
    LinksUrlService,
)


class DimServicesFilter(django_filters.FilterSet):
    """Фильтр для модели DimServices (основные сервисы)."""
    search = django_filters.CharFilter(
        field_name='alias',
        lookup_expr='icontains',
        label='Сервис (псевдоним содержит)',
        widget=forms.TextInput(attrs={'placeholder': 'Введите часть псевдонима'})  # ИЗМЕНЕНО
    )

    type = django_filters.ModelChoiceFilter(
        queryset=DimServicesTypes.objects.all(),
        field_name='type',
        label='Тип сервиса',
        empty_label='Любой',
        widget=forms.Select(attrs={'class': 'form-control'})  # ИЗМЕНЕНО
    )

    user = django_filters.CharFilter(
        method='filter_by_user_name',
        label='Пользователь (логин содержит)',
        widget=forms.TextInput(attrs={'placeholder': 'Введите часть логина'})  # ИЗМЕНЕНО
    )

    role = django_filters.ModelChoiceFilter(
        queryset=DimRoles.objects.all(),
        field_name='role',  # или то поле, по которому фильтруете
        label='Роль',
        empty_label='Любая',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = DimServices
        fields = ['search', 'type', 'user', 'role']

    def filter_by_user_name(self, queryset, name, value):
        """Фильтр по имени пользователя (username) через DimProfile."""
        if not value or not value.strip():
            return queryset

        value = value.strip()
        profile_ids = DimProfile.objects.filter(
            user__username__icontains=value
        ).values_list('id', flat=True)

        if not profile_ids:
            return queryset.none()

        return queryset.filter(
            linkresponsibleperson__name_id__in=profile_ids
        ).distinct()

    def filter_by_role(self, queryset, name, value):
        """Фильтр по роли ответственного."""
        if not value:
            return queryset
        return queryset.filter(
            linkresponsibleperson__role=value
        ).distinct()


class LinksUrlServiceFilter(django_filters.FilterSet):
    """Фильтры для модели LinksUrlService (связи URL с сервисами)."""
    url = django_filters.CharFilter(
        field_name='url__url',
        lookup_expr='icontains',
        label='URL содержит',
        widget=forms.TextInput(attrs={'placeholder': 'Введите часть URL'})  # ИЗМЕНЕНО
    )

    link_name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Название ссылки содержит',
        widget=forms.TextInput(attrs={'placeholder': 'Введите часть названия'})  # ИЗМЕНЕНО
    )

    description = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Описание содержит',
        widget=forms.TextInput(attrs={'placeholder': 'Введите часть описания'})  # ИЗМЕНЕНО
    )

    stack = django_filters.ModelChoiceFilter(
        queryset=DimTechStack.objects.all(),
        label='Технологический стек',
        empty_label='Любой',
        widget=forms.Select(attrs={'class': 'form-control'})  # ИЗМЕНЕНО
    )

    stage = django_filters.ModelChoiceFilter(
        queryset=DimStage.objects.all(),
        label='Стадия проекта',
        empty_label='Любая',
        widget=forms.Select(attrs={'class': 'form-control'})  # ИЗМЕНЕНО
    )

    service = django_filters.ModelChoiceFilter(
        queryset=DimServices.objects.all(),
        label='Сервис',
        empty_label='Любой',
        widget=forms.Select(attrs={'class': 'form-control'})  # ИЗМЕНЕНО
    )

    class Meta:
        model = LinksUrlService
        fields = ['url', 'link_name', 'stack', 'stage', 'service', 'description']


class ServiceUserView(LoginRequiredMixin, FilterView):
    """Представление для фильтрации сервисов по пользователям и ролям."""
    model = DimServices
    filterset_class = DimServicesFilter
    template_name = 'app_services/services-user.html'
    context_object_name = 'services'
    paginate_by = 20

    def get_filterset_kwargs(self, filterset_class):
        """Обработка GET-параметров для фильтра."""
        kwargs = super().get_filterset_kwargs(filterset_class)
        data = kwargs.get('data')

        if data is not None:
            data = data.copy()
            for key in list(data.keys()):
                if data[key] == '':
                    del data[key]
            kwargs['data'] = data

        return kwargs

    def get_queryset(self):
        """Получение QuerySet с оптимизированной загрузкой связанных данных."""
        queryset = super().get_queryset()
        return queryset.prefetch_related(
            'type',
            'dimservicesname_set',
            'linkresponsibleperson_set__role',
            'linkresponsibleperson_set__name__user'
        ).order_by('alias')

    def get_context_data(self, **kwargs):
        """Добавление дополнительной информации в контекст."""
        context = super().get_context_data(**kwargs)

        context['debug_info'] = {
            'total_count': DimServices.objects.count(),
            'filtered_count': self.object_list.count(),
            'form_data': dict(self.request.GET),
        }

        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']

        for key in list(get_params.keys()):
            if get_params[key] == '':
                del get_params[key]

        if get_params:
            context['query_string'] = get_params.urlencode()

        return context
